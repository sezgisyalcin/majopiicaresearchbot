from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Figure:
    name: str
    period: str
    notes: str

ITALIAN_PAINTERS = [
    Figure("Giotto di Bondone", "medieval", "Proto-Renaissance painting"),
    Figure("Sandro Botticelli", "renaissance", "Early Renaissance"),
    Figure("Leonardo da Vinci", "renaissance", "High Renaissance"),
    Figure("Michelangelo Buonarroti", "renaissance", "High Renaissance"),
    Figure("Raphael", "renaissance", "High Renaissance"),
    Figure("Caravaggio", "baroque", "Baroque naturalism"),
    Figure("Artemisia Gentileschi", "baroque", "Baroque"),
    Figure("Amedeo Modigliani", "modern", "Modernism"),
    Figure("Giorgio de Chirico", "modern", "Metaphysical painting"),
]

ITALIAN_ARCHITECTS = [
    Figure("Filippo Brunelleschi", "renaissance", "Early Renaissance architecture"),
    Figure("Leon Battista Alberti", "renaissance", "Renaissance theory and practice"),
    Figure("Andrea Palladio", "renaissance", "Classical revival and proportion"),
    Figure("Gian Lorenzo Bernini", "baroque", "Baroque architecture and sculpture"),
    Figure("Francesco Borromini", "baroque", "Baroque architecture"),
    Figure("Gio Ponti", "modern", "Modern architecture and design"),
    Figure("Aldo Rossi", "contemporary", "Postwar architectural theory"),
    Figure("Renzo Piano", "contemporary", "Contemporary architecture"),
]

ITALIAN_PHILOSOPHERS = [
    Figure("Dante Alighieri", "medieval", "Poetry, theology, political thought"),
    Figure("Marsilio Ficino", "renaissance", "Renaissance Platonism"),
    Figure("Niccolò Machiavelli", "renaissance", "Political philosophy"),
    Figure("Giambattista Vico", "modern", "Philosophy of history"),
    Figure("Antonio Gramsci", "modern", "Political theory"),
    Figure("Umberto Eco", "modern", "Semiotics and philosophy of culture"),
    Figure("Giorgio Agamben", "contemporary", "Contemporary philosophy"),
]

BERKLEE_MODERN_FILTER = {"Ottorino Respighi","Luigi Dallapiccola","Luciano Berio","Luigi Nono"}
