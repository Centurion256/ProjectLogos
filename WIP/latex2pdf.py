from latex import build_pdf


def latex2pdf(data, output):
    """
    (str, str) -> None
    :param data: string of LaTeX document
    :param output: name of output file
    :return: None
    """
    pdf = build_pdf(data)
    with open(output, "wb") as file:
        pdf.save_to(file)

latex2pdf(r"\documentclass{article} \begin{document} Hello, world! \end{document}", "output.pdf")
