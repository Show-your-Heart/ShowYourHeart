from io import BytesIO

import cairosvg
from django.http import HttpResponse
from lxml import etree


def svg_to_png(svg_bytes: bytes, png_name):
    output_width: int = 512
    buf = BytesIO()
    cairosvg.svg2png(bytestring=svg_bytes, write_to=buf, output_width=output_width)

    return buf.getvalue()


def get_png_stamp(vat_number, svg_network_stamp):
    # NOTE: the png won't have the policy configured on the svg
    # in order to have it, the policy must be installed on the docker container
    nif_placeholder = "entity-vat"

    # Parse svg to get the entity-vat node
    tree = etree.parse(svg_network_stamp)
    node = tree.xpath(f'//*[@id="{nif_placeholder}"]')

    if not node:
        raise Exception("node does not exist")
    node = node[0]

    node.text = vat_number
    raw = etree.tostring(tree, encoding="unicode")

    png = svg_to_png(raw, vat_number)

    return HttpResponse(png, content_type="image/png")
