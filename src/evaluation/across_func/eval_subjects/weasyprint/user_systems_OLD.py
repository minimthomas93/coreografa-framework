import weasyprint
import os

def weasyprint_fn(output):
    output_path = "eval_results/pdfs/testhtml.pdf"

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Generate PDF
    weasyprint.HTML(
        string=str(output),
        base_url="C:/Users/91996/Documents/GitHub/coreografa/src/evaluation/across_func").write_pdf(output_path)


#def weasyprint_fn(output):
    #weasyprint.HTML(string=str(output),base_url="C:/Users/91996/Documents/GitHub/coreografa/src/evaluation/across_func").write_pdf("eval_results/pdfs/testhtml.pdf")
