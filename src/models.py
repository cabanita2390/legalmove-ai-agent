from typing import List
from pydantic import BaseModel, Field

class ContractChangeOutput(BaseModel):
    """
    Representa el resultado final estructurado de la extracción de cambios 
    entre un contrato original y su enmienda o adenda.
    """
    sections_changed: List[str] = Field(
        ..., 
        description="Identificadores o nombres de las cláusulas/secciones modificadas o afectadas."
    )
    topics_touched: List[str] = Field(
        ..., 
        description="Categorías legales o comerciales afectadas por los cambios (ej. Penalidades, Vigencia, Precio, Confidencialidad)."
    )
    summary_of_the_change: str = Field(
        ..., 
        description="Descripción ejecutiva y clara de los cambios detectados en el contrato."
    )
