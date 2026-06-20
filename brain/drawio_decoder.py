"""
Décode le format draw.io compressé : <diagram> contient base64(deflate(XML))
Les fichiers avec `compressed="false"` stockent le XML brut directement.
"""

import base64
import re
import urllib.parse
import zlib


def decode_drawio(data: str) -> str | None:
    """Décode le contenu d'un fichier draw.io (compressed ou non) et retourne le <mxGraphModel>"""

    # Cas 1 : mxGraphModel directement dans le fichier
    m = re.search(r'<mxGraphModel[^>]*>.*?</mxGraphModel>', data, re.DOTALL)
    if m:
        return m.group()

    # Cas 2 : chercher dans les balises <diagram> (format compressé ou non)
    diagrams = re.findall(r'<diagram[^>]*>(.*?)</diagram>', data, re.DOTALL)
    for inner in diagrams:
        inner = inner.strip()

        # Si c'est du XML brut
        m2 = re.search(r'<mxGraphModel[^>]*>.*?</mxGraphModel>', inner, re.DOTALL)
        if m2:
            return m2.group()

        # Si c'est du contenu compressé (deflate + base64)
        try:
            # Les fichiers draw.io utilisent inflation (deflate) avec en-tête raw
            # et sont souvent URL-encoded en +
            raw = inner.strip().replace("&#xa;", "\n")
            
            # Essayer de décoder comme base64
            decoded_bytes = base64.b64decode(raw)
            
            # Essayer toutes les variantes de décompression draw.io
            # draw.io utilise raw deflate (wbits=-15) — pas d'en-tête zlib
            for wbits in [-zlib.MAX_WBITS, 15, 31]:
                try:
                    xml_bytes = zlib.decompress(decoded_bytes, wbits)
                    break
                except zlib.error:
                    continue
            else:
                continue
            
            xml_str = xml_bytes.decode("utf-8", errors="replace")
            # draw.io URL-encode le XML après deflate
            xml_str = urllib.parse.unquote(xml_str)
            m3 = re.search(r'<mxGraphModel[^>]*>.*?</mxGraphModel>', xml_str, re.DOTALL)
            if m3:
                return m3.group()
        except Exception:
            continue

    return None


def decode_and_clean(url_content: str) -> str | None:
    """Décode et nettoie un fichier draw.io complet"""
    xml = decode_drawio(url_content)
    if xml:
        # Nettoyer les espaces superflus
        xml = re.sub(r'>\s+<', '><', xml.strip())
    return xml