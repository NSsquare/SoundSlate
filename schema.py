from pydantic import BaseModel, Field


class KeyValue(BaseModel):
    # One labeled fact from the image, such as a bar's height
    label: str = Field(description="What the value belongs to, e.g. 'July' or 'Box A'")
    value: str = Field(description="The value exactly as shown, with units, e.g. '310 mm'")


class ImageDescription(BaseModel):
    # The full structured description of one image
    image_type: str = Field(
        description="One of: bar_chart, line_chart, pie_chart, table, diagram, handwriting, other"
    )
    summary: str = Field(description="One short sentence saying what the image shows")
    details: list[str] = Field(
        description="Important details in a sensible reading order, one short sentence each"
    )
    key_values: list[KeyValue] = Field(
        description="Specific labels and numbers that are clearly readable; empty list if none"
    )
    trend: str = Field(
        description="The main takeaway or trend; empty string if there is none"
    )
    confidence_notes: str = Field(
        description="Anything blurry, cut off, or uncertain; say 'None' if everything is clear"
    )