import csv
import os
from typing import Dict, Optional


class AdAggregator:
    """
    Aggregates ad campaign metrics from CSV files using streaming approach.
    
    Sums impressions, clicks, spend, and conversions grouped by campaign_id.
    Uses memory-efficient row-by-row processing via csv.DictReader.
    """
    
    def __init__(self) -> None:
        self._results: Dict[str, Dict[str, float]] = {}
        self._metrics: Dict[str, Dict[str, Optional[float]]] = {}
    
    def aggregate(self, filepath: str) -> Dict[str, Dict[str, float]]:
        """
        Stream through CSV file and aggregate metrics by campaign_id.
        
        Args:
            filepath: Path to the CSV file to process.
            
        Returns:
            Dictionary mapping campaign_id to aggregated metrics:
            {
                'CMP001': {'impressions': 1000, 'clicks': 50, 'spend': 100.5, 'conversions': 5},
                ...
            }
        """
        self._results.clear()
        self._metrics.clear()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                campaign_id = row['campaign_id']
                
                # Initialize campaign entry if first occurrence
                if campaign_id not in self._results:
                    self._results[campaign_id] = {
                        'impressions': 0.0,
                        'clicks': 0.0,
                        'spend': 0.0,
                        'conversions': 0.0
                    }
                
                # Aggregate metrics (date column ignored for speed)
                self._results[campaign_id]['impressions'] += int(row['impressions'])
                self._results[campaign_id]['clicks'] += int(row['clicks'])
                self._results[campaign_id]['spend'] += float(row['spend'])
                self._results[campaign_id]['conversions'] += int(row['conversions'])
        
        return self._results
    
    def get_results(self) -> Dict[str, Dict[str, float]]:
        """
        Return the current aggregation results.
        
        Returns:
            Dictionary of aggregated metrics by campaign_id.
        """
        return self._results
    
    def get_campaign_total(self, campaign_id: str) -> Dict[str, float] | None:
        """
        Get aggregated totals for a specific campaign.
        
        Args:
            campaign_id: The campaign identifier to look up.
            
        Returns:
            Dictionary of metrics for the campaign, or None if not found.
        """
        return self._results.get(campaign_id)
    
    def compute_metrics(self) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Calculate CTR and CPA for all campaigns.
        
        CTR (Click-Through Rate) = clicks / impressions
        CPA (Cost Per Acquisition) = spend / conversions
        
        Edge Cases:
            - If impressions == 0: CTR = 0.0
            - If conversions == 0: CPA = None (excluded from rankings)
        
        Returns:
            Dictionary mapping campaign_id to computed metrics:
            {
                'CMP001': {'ctr': 0.0275, 'cpa': 12.5},
                'CMP002': {'ctr': 0.0150, 'cpa': None},  # No conversions
                ...
            }
        """
        self._metrics.clear()
        
        for campaign_id, data in self._results.items():
            impressions = data['impressions']
            clicks = data['clicks']
            spend = data['spend']
            conversions = data['conversions']
            
            # Calculate CTR (handle division by zero)
            ctr = (clicks / impressions) if impressions > 0 else 0.0
            
            # Calculate CPA (None if no conversions to exclude from rankings)
            cpa = (spend / conversions) if conversions > 0 else None
            
            self._metrics[campaign_id] = {
                'ctr': round(ctr, 4),
                'cpa': round(cpa, 4) if cpa is not None else None
            }
        
        return self._metrics
    
    def get_metrics(self) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Return the computed metrics (CTR, CPA).
        
        Returns:
            Dictionary of computed metrics by campaign_id.
        """
        return self._metrics
    
    def write_reports(self, output_dir: str) -> None:
        """
        Generate CSV reports for top campaigns.
        
        Creates two files:
            - top10_ctr.csv: Top 10 campaigns by CTR (descending)
            - top10_cpa.csv: Top 10 campaigns by CPA (ascending, excludes 0 conversions)
        
        Args:
            output_dir: Directory path to write the report files.
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Ensure metrics are computed
        if not self._metrics:
            self.compute_metrics()
        
        # Prepare data with all fields for reports
        report_data = []
        for campaign_id, metrics in self._metrics.items():
            raw = self._results[campaign_id]
            report_data.append({
                'campaign_id': campaign_id,
                'impressions': int(raw['impressions']),
                'clicks': int(raw['clicks']),
                'spend': round(raw['spend'], 4),
                'conversions': int(raw['conversions']),
                'ctr': metrics['ctr'],
                'cpa': metrics['cpa']
            })
        
        # Top 10 by CTR (descending)
        top10_ctr = sorted(report_data, key=lambda x: x['ctr'], reverse=True)[:10]
        ctr_path = os.path.join(output_dir, 'top10_ctr.csv')
        self._write_csv(ctr_path, top10_ctr)
        print(f"Written: {ctr_path}")
        
        # Top 10 by CPA (ascending) - Filter out campaigns with 0 conversions (cpa=None)
        valid_cpa = [r for r in report_data if r['cpa'] is not None]
        top10_cpa = sorted(valid_cpa, key=lambda x: x['cpa'])[:10]
        cpa_path = os.path.join(output_dir, 'top10_cpa.csv')
        self._write_csv(cpa_path, top10_cpa)
        print(f"Written: {cpa_path}")
    
    def _write_csv(self, filepath: str, data: list) -> None:
        """
        Write data to a CSV file.
        
        Args:
            filepath: Path to the output CSV file.
            data: List of dictionaries to write.
        """
        if not data:
            return
        
        fieldnames = ['campaign_id', 'total_impressions', 'total_clicks', 'total_spend', 'total_conversions', 'CTR', 'CPA']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                # Map internal keys to new column names
                w_row = {
                    'campaign_id': row['campaign_id'],
                    'total_impressions': row['impressions'],
                    'total_clicks': row['clicks'],
                    'total_spend': row['spend'],
                    'total_conversions': row['conversions'],
                    'CTR': row['ctr'],
                    'CPA': row['cpa']
                }
                writer.writerow(w_row)


def main() -> None:
    """
    CLI entry point for the Ad Aggregator.
    
    Usage:
        python aggregator.py --input ad_data.csv --output output
    """
    import argparse
    import time
    import tracemalloc
    from pathlib import Path
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Aggregate ad campaign data and generate reports.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python aggregator.py --input ad_data.csv --output output
  python aggregator.py -i data.csv -o reports
        '''
    )
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Path to the input CSV file'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output',
        help='Directory to write report files (default: output)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        return
    
    # Get file size for summary
    file_size_bytes = input_path.stat().st_size
    file_size_mb = file_size_bytes / (1024 ** 2)
    file_size_gb = file_size_bytes / (1024 ** 3)
    
    # Start benchmarking
    tracemalloc.start()
    start_time = time.perf_counter()
    
    print("=" * 60)
    print("AD CAMPAIGN AGGREGATOR")
    print("=" * 60)
    print(f"Input:  {args.input} ({file_size_mb:.2f} MB)")
    print(f"Output: {args.output}/")
    print("-" * 60)
    
    # Process data
    aggregator = AdAggregator()
    
    print("\n[1/3] Aggregating data...")
    results = aggregator.aggregate(args.input)
    print(f"      Found {len(results)} campaigns")
    
    print("\n[2/3] Computing metrics (CTR, CPA)...")
    aggregator.compute_metrics()
    print("      Done")
    
    print("\n[3/3] Writing reports...")
    aggregator.write_reports(args.output)
    
    # Stop benchmarking
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Calculate benchmarks
    elapsed_time = end_time - start_time
    peak_memory_mb = peak / (1024 ** 2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    
    if file_size_gb >= 1:
        print(f"Processed {file_size_gb:.2f}GB in {elapsed_time:.2f}s, Peak Memory: {peak_memory_mb:.2f}MB")
    else:
        print(f"Processed {file_size_mb:.2f}MB in {elapsed_time:.2f}s, Peak Memory: {peak_memory_mb:.2f}MB")
    
    print(f"Throughput: {file_size_mb / elapsed_time:.2f} MB/s")
    print("=" * 60)


if __name__ == "__main__":
    main()
