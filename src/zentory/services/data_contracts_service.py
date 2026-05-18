from zentory.schemas.platform_modules import DataContract, DataContractField, DataContractsReport


class DataContractsService:
    def build_report(self) -> DataContractsReport:
        return DataContractsReport(
            contracts=[
                DataContract(
                    name="sku_daily_snapshot",
                    version="1.0",
                    owner="sku_intelligence",
                    fields=[
                        DataContractField(
                            name="sku", field_type="str", description="Internal SKU id"
                        ),
                        DataContractField(
                            name="marketplace",
                            field_type="str",
                            description="WB/Ozon/YM source",
                        ),
                        DataContractField(
                            name="stock_units",
                            field_type="int",
                            description="Available stock",
                        ),
                        DataContractField(
                            name="drr_percent",
                            field_type="float",
                            description="Ad spend ratio",
                        ),
                    ],
                    safety_constraints=[
                        "No real marketplace writes",
                        "Tenant data must stay isolated",
                    ],
                ),
                DataContract(
                    name="action_recommendation",
                    version="1.0",
                    owner="action_center",
                    fields=[
                        DataContractField(
                            name="action_id", field_type="str", description="Approval id"
                        ),
                        DataContractField(
                            name="risk_level", field_type="str", description="Safety risk"
                        ),
                        DataContractField(
                            name="rollback_available",
                            field_type="bool",
                            description="Rollback flag",
                        ),
                    ],
                    safety_constraints=[
                        "High-risk actions require approval",
                        "Keep rollback metadata",
                    ],
                ),
            ]
        )
