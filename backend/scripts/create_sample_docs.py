import os
from pathlib import Path

def create_simple_pdf(output_path: Path, title: str, pages_content: list):
    """
    Creates a valid PDF file directly with raw PDF syntax (no third-party dependencies required).
    """
    objects = []
    
    def add_object(content):
        objects.append(content)
        return len(objects)

    # 1: Catalog
    catalog_id = add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
    
    # Page object IDs will be added later
    # 2: Pages container (placeholder, will format at the end)
    pages_id = add_object(b"") 
    
    # 3: Font
    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    page_refs = []
    for content_text in pages_content:
        # Stream content
        stream_lines = [
            "BT",
            "/F1 14 Tf",
            "50 750 Td",
            f"({title}) Tj",
            "/F1 10 Tf",
            "0 -30 Td",
        ]
        for line in content_text.splitlines():
            # escape parenthesis
            safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream_lines.append(f"({safe_line}) Tj")
            stream_lines.append("0 -16 Td")
        stream_lines.append("ET")
        stream_bytes = "\n".join(stream_lines).encode("latin-1", "replace")
        
        content_id = add_object(
            b"<< /Length " + str(len(stream_bytes)).encode() + b" >>\nstream\n" +
            stream_bytes + b"\nendstream"
        )
        
        page_id = add_object(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>".encode()
        )
        page_refs.append(f"{page_id} 0 R")

    # Update Pages object (index 1)
    kids_str = " ".join(page_refs)
    objects[1] = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_refs)} >>".encode()

    # Write file
    with open(output_path, "wb") as f:
        f.write(b"%PDF-1.4\n")
        offsets = []
        for idx, obj in enumerate(objects, start=1):
            offsets.append(f.tell())
            f.write(f"{idx} 0 obj\n".encode())
            f.write(obj)
            f.write(b"\nendobj\n")
        
        xref_pos = f.tell()
        f.write(b"xref\n")
        f.write(f"0 {len(objects) + 1}\n".encode())
        f.write(b"0000000000 65535 f \n")
        for off in offsets:
            f.write(f"{off:010d} 00000 n \n".encode())
        
        f.write(b"trailer\n")
        f.write(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode())
        f.write(b"startxref\n")
        f.write(f"{xref_pos}\n".encode())
        f.write(b"%%EOF\n")

if __name__ == "__main__":
    samples_dir = Path(__file__).resolve().parent.parent / "data" / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    # 1. Company Leave Policy
    leave_pages = [
        "Section 1: Company Annual Leave Policy\n"
        "All permanent employees are entitled to 20 business days of paid annual leave per calendar year.\n"
        "Leave requests exceeding 5 consecutive days must be submitted at least 2 weeks in advance.\n"
        "Unused annual leave up to 8 days can be carried forward to the subsequent financial year.",
        
        "Clause 4.2: Maternity and Paternity Leave Provisions\n"
        "Female employees with at least 80 days of continuous service are eligible for 26 weeks of fully paid maternity leave.\n"
        "Maternity leave can commence up to 8 weeks prior to the expected date of delivery.\n"
        "Male employees are entitled to 15 days of paid paternity leave within the first 6 months of childbirth."
    ]
    create_simple_pdf(samples_dir / "Company_Leave_Policy.pdf", "GLOBAL ENTERPRISE LEAVE POLICY", leave_pages)

    # 2. IT Security Protocol
    it_pages = [
        "Section 2.1: Password and Access Control Protocols\n"
        "All employee accounts must enforce complex passwords containing at least 12 characters.\n"
        "Passwords expire every 90 days and cannot be reused across the last 6 iterations.\n"
        "Two-factor authentication (2FA) is mandatory for accessing internal corporate systems.",
        
        "Clause 5.3: Lost or Stolen Company Hardware\n"
        "In the event of a lost or stolen laptop or mobile device, the employee must notify IT Security within 2 hours.\n"
        "Remote device wipe will be initiated immediately by the IT administrator to prevent data leaks."
    ]
    create_simple_pdf(samples_dir / "IT_Security_Protocol.pdf", "CORPORATE IT SECURITY PROTOCOL", it_pages)

    # 3. Physics Textbook (Class 10)
    physics_pages = [
        "Chapter 12: Electricity and Circuits\n"
        "Electric current is defined as the rate of flow of electric charge across a conductor.\n"
        "If a net charge Q flows across any cross-section of a conductor in time t, then current I = Q / t.\n"
        "The SI unit of electric charge is Coulomb (C), and the SI unit of electric current is Ampere (A).",

        "Section 12.2: Ohms Law and Resistance\n"
        "According to Ohms Law, the electric current flowing through a metallic conductor is directly proportional\n"
        "to the potential difference across its terminals, provided temperature remains constant.\n"
        "Formula: V = I * R, where R is the resistance of the conductor measured in Ohms."
    ]
    create_simple_pdf(samples_dir / "Physics_Class10_Electricity.pdf", "NCERT PHYSICS CLASS 10", physics_pages)

    print(f"Sample PDF documents generated successfully in: {samples_dir}")
