"""
Test suite for AdAggregator class.
Uses pytest fixtures to create temporary CSV test data.
"""

import os
import pytest
import tempfile
from aggregator import AdAggregator


# Sample test data matching the exact specification
SAMPLE_DATA = """campaign_id,date,impressions,clicks,spend,conversions
CMP025,2025-04-18,3653,60,64.29,2
CMP020,2025-05-03,24465,764,1394.62,42
CMP019,2025-02-05,7214,236,135.93,21
"""


@pytest.fixture
def temp_csv_file():
    """
    Create a temporary CSV file with sample data.
    
    Yields:
        str: Path to the temporary CSV file.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(SAMPLE_DATA)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def aggregator_with_data(temp_csv_file):
    """
    Create an AdAggregator instance with sample data loaded.
    
    Args:
        temp_csv_file: Fixture providing the temp CSV path.
        
    Returns:
        AdAggregator: Aggregator with data already loaded.
    """
    aggregator = AdAggregator()
    aggregator.aggregate(temp_csv_file)
    aggregator.compute_metrics()
    return aggregator


class TestDataAccuracy:
    """Tests for data accuracy after aggregation."""
    
    def test_cmp025_impressions(self, aggregator_with_data):
        """Verify CMP025 impressions = 3653."""
        result = aggregator_with_data.get_campaign_total('CMP025')
        assert result is not None
        assert result['impressions'] == 3653
    
    def test_cmp025_clicks(self, aggregator_with_data):
        """Verify CMP025 clicks = 60."""
        result = aggregator_with_data.get_campaign_total('CMP025')
        assert result is not None
        assert result['clicks'] == 60
    
    def test_cmp020_spend(self, aggregator_with_data):
        """Verify CMP020 spend = 1394.62."""
        result = aggregator_with_data.get_campaign_total('CMP020')
        assert result is not None
        assert abs(result['spend'] - 1394.62) < 0.01
    
    def test_cmp019_conversions(self, aggregator_with_data):
        """Verify CMP019 conversions = 21."""
        result = aggregator_with_data.get_campaign_total('CMP019')
        assert result is not None
        assert result['conversions'] == 21


class TestLogicCheck:
    """Tests for CTR and CPA calculation logic."""
    
    def test_cmp025_ctr_calculation(self, aggregator_with_data):
        """Verify CTR calculation for CMP025 (60/3653)."""
        metrics = aggregator_with_data.get_metrics()
        expected_ctr = round(60 / 3653, 4)
        assert metrics['CMP025']['ctr'] == expected_ctr
    
    def test_cmp020_cpa_calculation(self, aggregator_with_data):
        """Verify CPA calculation for CMP020 (1394.62/42)."""
        metrics = aggregator_with_data.get_metrics()
        expected_cpa = round(1394.62 / 42, 4)
        assert metrics['CMP020']['cpa'] == expected_cpa
    
    def test_ctr_formula(self, aggregator_with_data):
        """Verify CTR = clicks / impressions for all campaigns."""
        results = aggregator_with_data.get_results()
        metrics = aggregator_with_data.get_metrics()
        
        for campaign_id, data in results.items():
            expected_ctr = round(data['clicks'] / data['impressions'], 4)
            assert metrics[campaign_id]['ctr'] == expected_ctr
    
    def test_cpa_formula(self, aggregator_with_data):
        """Verify CPA = spend / conversions for campaigns with conversions > 0."""
        results = aggregator_with_data.get_results()
        metrics = aggregator_with_data.get_metrics()
        
        for campaign_id, data in results.items():
            if data['conversions'] > 0:
                expected_cpa = round(data['spend'] / data['conversions'], 4)
                assert metrics[campaign_id]['cpa'] == expected_cpa


class TestIntegration:
    """Integration tests for end-to-end processing."""
    
    def test_aggregator_runs_without_crash(self, temp_csv_file):
        """Ensure the aggregator runs through the file without crashing."""
        aggregator = AdAggregator()
        
        # Should not raise any exceptions
        results = aggregator.aggregate(temp_csv_file)
        metrics = aggregator.compute_metrics()
        
        # Verify we got results
        assert len(results) == 3
        assert len(metrics) == 3
    
    def test_all_campaigns_present(self, aggregator_with_data):
        """Verify all campaigns from sample data are present."""
        results = aggregator_with_data.get_results()
        expected_campaigns = {'CMP025', 'CMP020', 'CMP019'}
        assert set(results.keys()) == expected_campaigns
    
    def test_write_reports_creates_files(self, aggregator_with_data):
        """Verify write_reports creates the expected output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aggregator_with_data.write_reports(temp_dir)
            
            ctr_path = os.path.join(temp_dir, 'top10_ctr.csv')
            cpa_path = os.path.join(temp_dir, 'top10_cpa.csv')
            
            assert os.path.exists(ctr_path), "top10_ctr.csv should be created"
            assert os.path.exists(cpa_path), "top10_cpa.csv should be created"


class TestEdgeCases:
    """Tests for edge case handling."""
    
    def test_zero_conversions_cpa_is_none(self):
        """Verify CPA is None when conversions = 0."""
        # Create test data with zero conversions
        zero_conv_data = """campaign_id,date,impressions,clicks,spend,conversions
CMP_ZERO,2025-01-01,1000,50,100.00,0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(zero_conv_data)
            temp_path = f.name
        
        try:
            aggregator = AdAggregator()
            aggregator.aggregate(temp_path)
            metrics = aggregator.compute_metrics()
            
            assert metrics['CMP_ZERO']['cpa'] is None
        finally:
            os.unlink(temp_path)
    
    def test_zero_impressions_ctr_is_zero(self):
        """Verify CTR is 0 when impressions = 0."""
        # Create test data with zero impressions
        zero_imp_data = """campaign_id,date,impressions,clicks,spend,conversions
CMP_ZERO,2025-01-01,0,0,100.00,5
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(zero_imp_data)
            temp_path = f.name
        
        try:
            aggregator = AdAggregator()
            aggregator.aggregate(temp_path)
            metrics = aggregator.compute_metrics()
            
            assert metrics['CMP_ZERO']['ctr'] == 0.0
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
