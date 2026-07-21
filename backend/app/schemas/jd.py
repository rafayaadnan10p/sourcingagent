from pydantic import BaseModel, field_validator

VALID_PLATFORMS = {"all", "linkedin", "github", "upwork", "fiverr", "behance"}
MAX_JD_LENGTH = 50_000  # characters
VALID_LOCATIONS = {"not_specified", "Karachi", "Lahore", "Islamabad"}


class JDTextInput(BaseModel):
    jd_text: str
    platform_scope: str = "linkedin"
    location_override: str = "not_specified"   # overrides JD location if set
    target_companies: str = ""                 # comma-separated company names
    open_to_work: bool = False                 # LinkedIn: filter for #OpenToWork profiles

    @field_validator("jd_text")
    @classmethod
    def jd_text_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("JD text cannot be empty")
        if len(v) > MAX_JD_LENGTH:
            raise ValueError(f"JD text exceeds maximum length of {MAX_JD_LENGTH} characters")
        return v

    @field_validator("platform_scope")
    @classmethod
    def platform_scope_valid(cls, v: str) -> str:
        if v not in VALID_PLATFORMS:
            raise ValueError(f"platform_scope must be one of {sorted(VALID_PLATFORMS)}")
        return v

    @field_validator("location_override")
    @classmethod
    def location_override_valid(cls, v: str) -> str:
        if v not in VALID_LOCATIONS:
            raise ValueError(f"location_override must be one of {sorted(VALID_LOCATIONS)}")
        return v
