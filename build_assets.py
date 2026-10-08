"""Generate the complete revised publication figure set."""
from build_integrated_assets import b, figures

if __name__ == "__main__":
    b.base_figures()
    b.diagrams()
    b.revision_figures()
    figures()
