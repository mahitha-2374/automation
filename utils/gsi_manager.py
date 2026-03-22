"""
GSI Manager - Handle GSI ID retrieval and data filtering
Extracts GSI information from CSV columns and retrieves related data
"""

import pandas as pd
from typing import Dict, List, Any, Optional


class GSIManager:
    """Manage GSI (Global System Identifier) operations"""

    def __init__(self):
        """Initialize GSI Manager"""
        self.gsi_data = {}
        self.gsi_column_name = None
        self.detected_gsi_columns = []

    def detect_gsi_column(self, user_df: pd.DataFrame, role_df: pd.DataFrame) -> List[str]:
        """
        Auto-detect potential GSI columns in the dataframes
        
        Looks for columns with names like:
        - *gsi*, *app*, *system*, *application*, *enterprise*
        
        Args:
            user_df: User export dataframe
            role_df: Role export dataframe
            
        Returns:
            List of potential GSI column names
        """
        potential_columns = []
        
        # Common GSI column patterns
        gsi_patterns = ['gsi', 'app', 'system', 'application', 'enterprise', 
                        'system_id', 'app_id', 'application_id', 'gsi_id']
        
        for df, df_name in [(user_df, "user"), (role_df, "role")]:
            for col in df.columns:
                col_lower = col.lower()
                for pattern in gsi_patterns:
                    if pattern in col_lower:
                        potential_columns.append(col)
                        break
        
        self.detected_gsi_columns = list(set(potential_columns))
        return self.detected_gsi_columns

    def set_gsi_column(self, column_name: str):
        """
        Set which column contains the GSI ID
        
        Args:
            column_name: Name of the GSI column
        """
        self.gsi_column_name = column_name

    def extract_gsi_data(self, user_df: pd.DataFrame, role_df: pd.DataFrame, 
                        gsi_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract GSI-specific data from the dataframes
        
        Args:
            user_df: User export dataframe
            role_df: Role export dataframe
            gsi_column: Column name containing GSI ID
            
        Returns:
            Dictionary with GSI information and related data
        """
        if gsi_column:
            self.gsi_column_name = gsi_column
        
        if not self.gsi_column_name:
            return self._create_default_gsi_data(user_df, role_df)
        
        gsi_data = {}
        
        # Extract unique GSI IDs
        unique_gsis = set()
        
        if self.gsi_column_name in user_df.columns:
            unique_gsis.update(user_df[self.gsi_column_name].dropna().unique())
        
        if self.gsi_column_name in role_df.columns:
            unique_gsis.update(role_df[self.gsi_column_name].dropna().unique())
        
        # Build GSI data structure
        for gsi_id in unique_gsis:
            gsi_data[str(gsi_id)] = {
                "gsi_id": str(gsi_id),
                "users": [],
                "roles": [],
                "entitlements": [],
                "user_count": 0,
                "role_count": 0,
                "entitlement_count": 0,
                "user_role_mappings": 0,
                "role_resource_mappings": 0
            }
        
        # Populate GSI-specific data
        for _, row in user_df.iterrows():
            gsi_id = str(row.get(self.gsi_column_name, "Unknown"))
            if gsi_id in gsi_data:
                gsi_data[gsi_id]["users"].append(row.to_dict())
                gsi_data[gsi_id]["user_count"] += 1
        
        for _, row in role_df.iterrows():
            gsi_id = str(row.get(self.gsi_column_name, "Unknown"))
            if gsi_id in gsi_data:
                gsi_data[gsi_id]["roles"].append(row.to_dict())
                gsi_data[gsi_id]["role_count"] += 1
        
        self.gsi_data = gsi_data
        return gsi_data

    def get_gsi_by_id(self, gsi_id: str) -> Dict[str, Any]:
        """
        Get data for a specific GSI ID
        
        Args:
            gsi_id: The GSI ID to retrieve
            
        Returns:
            Dictionary with GSI data or empty dict if not found
        """
        return self.gsi_data.get(str(gsi_id), {})

    def filter_data_by_gsi(self, user_df: pd.DataFrame, role_df: pd.DataFrame,
                          gsi_id: str) -> tuple:
        """
        Filter user and role dataframes by GSI ID
        
        Args:
            user_df: Original user dataframe
            role_df: Original role dataframe
            gsi_id: GSI ID to filter by
            
        Returns:
            Tuple of (filtered_user_df, filtered_role_df)
        """
        if not self.gsi_column_name:
            return user_df, role_df
        
        filtered_user = user_df[user_df[self.gsi_column_name].astype(str) == str(gsi_id)]
        filtered_role = role_df[role_df[self.gsi_column_name].astype(str) == str(gsi_id)]
        
        return filtered_user, filtered_role

    def get_all_gsi_ids(self) -> List[str]:
        """
        Get list of all GSI IDs found in data
        
        Returns:
            List of GSI IDs
        """
        return list(self.gsi_data.keys())

    def get_gsi_summary(self, gsi_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a GSI
        
        Args:
            gsi_id: The GSI ID
            
        Returns:
            Dictionary with summary stats
        """
        gsi_info = self.get_gsi_by_id(gsi_id)
        
        return {
            "gsi_id": gsi_id,
            "total_users": gsi_info.get("user_count", 0),
            "total_roles": gsi_info.get("role_count", 0),
            "total_entitlements": gsi_info.get("entitlement_count", 0),
            "user_role_mappings": gsi_info.get("user_role_mappings", 0),
            "description": f"GSI Application: {gsi_id}"
        }

    def _create_default_gsi_data(self, user_df: pd.DataFrame, 
                                 role_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Create default GSI data when no GSI column is found
        
        Args:
            user_df: User dataframe
            role_df: Role dataframe
            
        Returns:
            Default GSI data structure
        """
        return {
            "default": {
                "gsi_id": "default",
                "users": user_df.to_dict('records'),
                "roles": role_df.to_dict('records'),
                "entitlements": [],
                "user_count": len(user_df),
                "role_count": len(role_df),
                "entitlement_count": 0
            }
        }
