from enum import Enum


class OcsfVersion(Enum):
    """
    Supported OCSF schema versions.
    See https://schema.ocsf.io/ for version details.
    """
    V1_0_0 = "1.0.0"
    V1_1_0 = "1.1.0"
    V1_2_0 = "1.2.0"
    V1_3_0 = "1.3.0"
    V1_4_0 = "1.4.0"
    V1_5_0 = "1.5.0"
    V1_6_0 = "1.6.0"
    V1_7_0 = "1.7.0"  # Current stable version

    @classmethod
    def get_default(cls):
        """Returns the default/recommended OCSF version"""
        return cls.V1_1_0  # Keep v1.1.0 as default for backward compatibility

    @classmethod
    def get_latest(cls):
        """Returns the latest stable OCSF version"""
        return cls.V1_7_0

    def get_url_safe_name(self):
        """Returns URL-safe version string (e.g., v1_1_0)"""
        return f"v{self.value.replace('.', '_')}"
