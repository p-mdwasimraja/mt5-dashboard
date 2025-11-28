"""
MT5 Data Processor
Processes MT5 data from multiple sources and organizes into structured format
"""
import os
import pandas as pd
import yaml
import shutil
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MT5DataProcessor:
    """Process and organize MT5 data from multiple sources"""
    
    def __init__(self, config_path='config/settings.yaml'):
        """Initialize processor with config"""
        self.config = self._load_config(config_path)
        self.processed_path = Path(self.config['paths']['processed_data'])
        self.raw_path = Path(self.config['paths']['raw_data'])
        self.backup_path = Path(self.config['paths']['backup_data'])
        
    def _load_config(self, config_path):
        """Load YAML configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _ensure_directories(self):
        """Create necessary directories"""
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories in processed
        subdirs = ['accounts', 'deposits', 'transactions', 'positions', 'summary']
        for subdir in subdirs:
            (self.processed_path / subdir).mkdir(exist_ok=True)
        
        logger.info(f"Created directory structure in {self.processed_path}")
    
    def process_all_sources(self):
        """Process data from all enabled MT5 sources"""
        self._ensure_directories()
        
        sources = self.config.get('mt5_sources', [])
        all_accounts = []
        all_deposits = []
        all_transactions = []
        all_positions = []
        
        for source in sources:
            if not source.get('enabled', False):
                logger.info(f"Skipping disabled source: {source['name']}")
                continue
            
            logger.info(f"Processing source: {source['name']}")
            
            try:
                # Process each source
                accounts, deposits, transactions, positions = self._process_source(source)
                
                if accounts is not None:
                    all_accounts.append(accounts)
                if deposits is not None:
                    all_deposits.append(deposits)
                if transactions is not None:
                    all_transactions.append(transactions)
                if positions is not None:
                    all_positions.append(positions)
                    
            except Exception as e:
                logger.error(f"Error processing source {source['name']}: {e}")
                continue
        
        # Combine and save all data
        self._save_combined_data(all_accounts, all_deposits, all_transactions, all_positions)
        logger.info("Data processing complete!")
        
    def _process_source(self, source):
        """Process data from a single MT5 source"""
        source_path = Path(source['path'])
        source_name = source['name']
        
        if not source_path.exists():
            logger.warning(f"Source path does not exist: {source_path}")
            return None, None, None, None
        
        # Find all CSV files in the source
        account_files = list(source_path.glob('*_Account.csv'))
        history_files = list(source_path.glob('*_History.csv'))
        position_files = list(source_path.glob('*_Positions.csv'))
        
        logger.info(f"Found {len(account_files)} account, {len(history_files)} history, {len(position_files)} position files")
        
        # Process account data
        accounts_df = self._process_account_files(account_files, source_name)
        
        # Process history data (split into deposits and transactions)
        deposits_df, transactions_df = self._process_history_files(history_files, source_name)
        
        # Process position data
        positions_df = self._process_position_files(position_files, source_name)
        
        return accounts_df, deposits_df, transactions_df, positions_df
    
    def _process_account_files(self, files, source_name):
        """Process account CSV files"""
        if not files:
            return None
        
        dfs = []
        for file in files:
            try:
                df = pd.read_csv(file, sep=';')
                df['Source'] = source_name
                df['ProcessedTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                dfs.append(df)
                logger.info(f"Processed account file: {file.name}")
            except Exception as e:
                logger.error(f"Error reading {file.name}: {e}")
        
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            # Save individual EA files
            for ea_name in combined['EA_Name'].unique():
                ea_data = combined[combined['EA_Name'] == ea_name]
                output_file = self.processed_path / 'accounts' / f'{ea_name}_account.csv'
                ea_data.to_csv(output_file, index=False)
                logger.info(f"Saved account data: {output_file.name}")
            return combined
        return None
    
    def _process_history_files(self, files, source_name):
        """Process history CSV files and separate deposits from transactions"""
        if not files:
            return None, None
        
        all_data = []
        for file in files:
            try:
                df = pd.read_csv(file, sep=';')
                df['Source'] = source_name
                df['ProcessedTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                all_data.append(df)
                logger.info(f"Processed history file: {file.name}")
            except Exception as e:
                logger.error(f"Error reading {file.name}: {e}")
        
        if not all_data:
            return None, None
        
        combined = pd.concat(all_data, ignore_index=True)
        
        # Separate deposits (BALANCE type) from transactions (trades)
        deposits_df = combined[combined['Type'] == 'BALANCE'].copy()
        transactions_df = combined[combined['Type'] != 'BALANCE'].copy()
        
        # Save deposit data
        if not deposits_df.empty:
            for ea_name in deposits_df['EA_Name'].unique():
                ea_deposits = deposits_df[deposits_df['EA_Name'] == ea_name]
                output_file = self.processed_path / 'deposits' / f'{ea_name}_deposits.csv'
                ea_deposits.to_csv(output_file, index=False)
                logger.info(f"Saved deposit data: {output_file.name}")
        
        # Save transaction data
        if not transactions_df.empty:
            for ea_name in transactions_df['EA_Name'].unique():
                ea_transactions = transactions_df[transactions_df['EA_Name'] == ea_name]
                output_file = self.processed_path / 'transactions' / f'{ea_name}_transactions.csv'
                ea_transactions.to_csv(output_file, index=False)
                logger.info(f"Saved transaction data: {output_file.name}")
        
        return deposits_df, transactions_df
    
    def _process_position_files(self, files, source_name):
        """Process position CSV files"""
        if not files:
            return None
        
        dfs = []
        for file in files:
            try:
                df = pd.read_csv(file, sep=';')
                # Only process if there's actual position data
                if not df.empty and len(df.columns) > 1:
                    df['Source'] = source_name
                    df['ProcessedTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    dfs.append(df)
                    logger.info(f"Processed position file: {file.name}")
            except Exception as e:
                logger.error(f"Error reading {file.name}: {e}")
        
        if dfs:
            combined = pd.concat(dfs, ignore_index=True)
            # Save individual EA files
            for ea_name in combined['EA_Name'].unique():
                ea_data = combined[combined['EA_Name'] == ea_name]
                output_file = self.processed_path / 'positions' / f'{ea_name}_positions.csv'
                ea_data.to_csv(output_file, index=False)
                logger.info(f"Saved position data: {output_file.name}")
            return combined
        return None
    
    def _save_combined_data(self, accounts, deposits, transactions, positions):
        """Save combined data from all sources"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save combined accounts
        if accounts:
            combined_accounts = pd.concat(accounts, ignore_index=True)
            output_file = self.processed_path / 'summary' / f'all_accounts_{timestamp}.csv'
            combined_accounts.to_csv(output_file, index=False)
            
            # Also save latest
            latest_file = self.processed_path / 'summary' / 'all_accounts_latest.csv'
            combined_accounts.to_csv(latest_file, index=False)
            logger.info(f"Saved combined accounts: {output_file.name}")
        
        # Save combined deposits
        if deposits:
            combined_deposits = pd.concat(deposits, ignore_index=True)
            output_file = self.processed_path / 'summary' / f'all_deposits_{timestamp}.csv'
            combined_deposits.to_csv(output_file, index=False)
            
            latest_file = self.processed_path / 'summary' / 'all_deposits_latest.csv'
            combined_deposits.to_csv(latest_file, index=False)
            logger.info(f"Saved combined deposits: {output_file.name}")
        
        # Save combined transactions
        if transactions:
            combined_transactions = pd.concat(transactions, ignore_index=True)
            output_file = self.processed_path / 'summary' / f'all_transactions_{timestamp}.csv'
            combined_transactions.to_csv(output_file, index=False)
            
            latest_file = self.processed_path / 'summary' / 'all_transactions_latest.csv'
            combined_transactions.to_csv(latest_file, index=False)
            logger.info(f"Saved combined transactions: {output_file.name}")
        
        # Save combined positions
        if positions:
            combined_positions = pd.concat(positions, ignore_index=True)
            output_file = self.processed_path / 'summary' / f'all_positions_{timestamp}.csv'
            combined_positions.to_csv(output_file, index=False)
            
            latest_file = self.processed_path / 'summary' / 'all_positions_latest.csv'
            combined_positions.to_csv(latest_file, index=False)
            logger.info(f"Saved combined positions: {output_file.name}")
        
        # Create summary statistics
        self._create_summary_stats(accounts, deposits, transactions, positions)
    
    def _create_summary_stats(self, accounts, deposits, transactions, positions):
        """Create summary statistics file"""
        stats = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_eas': 0,
            'total_accounts': 0,
            'total_deposits': 0,
            'total_transactions': 0,
            'total_open_positions': 0,
            'eas': {}
        }
        
        if accounts:
            combined_accounts = pd.concat(accounts, ignore_index=True)
            ea_names = combined_accounts['EA_Name'].unique()
            stats['total_eas'] = len(ea_names)
            stats['total_accounts'] = len(combined_accounts)
            
            for ea in ea_names:
                ea_data = combined_accounts[combined_accounts['EA_Name'] == ea]
                latest = ea_data.iloc[-1] if not ea_data.empty else None
                
                stats['eas'][ea] = {
                    'balance': float(latest['Balance']) if latest is not None else 0,
                    'equity': float(latest['Equity']) if latest is not None else 0,
                    'profit': float(latest['Profit']) if latest is not None else 0,
                    'currency': str(latest['Currency']) if latest is not None else 'USD'
                }
        
        if deposits:
            combined_deposits = pd.concat(deposits, ignore_index=True)
            stats['total_deposits'] = len(combined_deposits)
        
        if transactions:
            combined_transactions = pd.concat(transactions, ignore_index=True)
            stats['total_transactions'] = len(combined_transactions)
        
        if positions:
            combined_positions = pd.concat(positions, ignore_index=True)
            stats['total_open_positions'] = len(combined_positions)
        
        # Save stats as JSON
        import json
        stats_file = self.processed_path / 'summary' / 'stats.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Saved summary statistics: {stats_file.name}")


def main():
    """Main entry point"""
    processor = MT5DataProcessor()
    processor.process_all_sources()


if __name__ == '__main__':
    main()
