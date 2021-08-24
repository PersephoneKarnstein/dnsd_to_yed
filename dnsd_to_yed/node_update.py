class Node:

    custom_properties_defs = {}

    def __init__(self, node_name, label=None, label_alignment="center", shape="rectangle", font_family="Dialog",
                 underlined_text="false", font_style="plain", font_size="12", font_color="#000000",
                 shape_fill="#FF0000", shape_fill2=None, transparent="false", border_color="#000000",
                 border_type="line", border_width="1.0", height=False, width=False, x=False,
                 y=False, node_type="ShapeNode", UML=False,
                 custom_properties=None, description="", url=""):

        self.label = label
        if label is None:
            self.label = node_name

        self.node_name = node_name

        self.node_type = node_type
        self.UML = UML

        self.parent = None

        # node shape
        if shape not in node_shapes:
            raise RuntimeWarning("Node shape %s not recognised" % shape)

        self.shape = shape

        # label formatting options
        self.font_family = font_family
        self.underlined_text = underlined_text

        if font_style not in font_styles:
            raise RuntimeWarning("Font style %s not recognised" % font_style)

        if label_alignment not in label_alignments:
            raise RuntimeWarning("Label alignment %s not recognised" % label_alignment)

        self.font_style = font_style
        self.font_size = font_size
        self.font_color = font_color

        self.label_alignment = label_alignment

        # shape fill
        self.shape_fill = shape_fill
        self.shape_fill2 = shape_fill2
        self.transparent = transparent

        # border options
        self.border_color = border_color
        self.border_width = border_width

        if border_type not in line_types:
            raise RuntimeWarning("Border type %s not recognised" % border_type)

        self.border_type = border_type

        # geometry
        self.geom = {}
        if height:
            self.geom["height"] = height
        if width:
            self.geom["width"] = width
        if x:
            self.geom["x"] = x
        if y:
            self.geom["y"] = y

        self.description = description
        self.url = url

        # Handle Node Custom Properties
        for name, definition in Node.custom_properties_defs.items():
            if custom_properties:
                for k, v in custom_properties.items():
                    if k not in Node.custom_properties_defs:
                        raise RuntimeWarning("key %s not recognised" % k)
                    if name == k:
                        setattr(self, name, custom_properties[k])
                        break
                else:
                    setattr(self, name, definition.default_value)
            else:
                setattr(self, name, definition.default_value)

    def convert(self):

        node = ET.Element("node", id=str(self.node_name))
        data = ET.SubElement(node, "data", key="data_node")
        shape = ET.SubElement(data, "y:" + self.node_type)

        if self.geom:
            ET.SubElement(shape, "y:Geometry", **self.geom)
        # <y:Geometry height="30.0" width="30.0" x="475.0" y="727.0"/>

        if self.shape_fill2:
            ET.SubElement(shape, "y:Fill", color=self.shape_fill, color2=self.shape_fill2,
                      transparent=self.transparent)
        else:
            ET.SubElement(shape, "y:Fill", color=self.shape_fill,
                      transparent=self.transparent)

        ET.SubElement(shape, "y:BorderStyle", color=self.border_color, type=self.border_type,
                      width=self.border_width)

        label = ET.SubElement(shape, "y:NodeLabel", fontFamily=self.font_family,
                              fontSize=self.font_size,
                              underlinedText=self.underlined_text,
                              fontStyle=self.font_style,
                              alignment=self.label_alignment,
                              textColor=self.font_color)
        label.text = self.label

        ET.SubElement(shape, "y:Shape", type=self.shape)

        if self.UML:
            UML = ET.SubElement(shape, "y:UML")

            attributes = ET.SubElement(UML, "y:AttributeLabel", type=self.shape)
            attributes.text = self.UML["attributes"]

            methods = ET.SubElement(UML, "y:MethodLabel", type=self.shape)
            methods.text = self.UML["methods"]

            stereotype = self.UML["stereotype"] if "stereotype" in self.UML else ""
            UML.set("stereotype", stereotype)

        if self.url:
            url_node = ET.SubElement(node, "data", key="url_node")
            url_node.text = self.url

        if self.description:
            description_node = ET.SubElement(node, "data", key="description_node")
            description_node.text = self.description

        # Node Custom Properties
        for name, definition in Node.custom_properties_defs.items():
            node_custom_prop = ET.SubElement(node, "data", key=definition.id)
            node_custom_prop.text = getattr(self, name)

        return node

    @classmethod
    def set_custom_properties_defs(cls, custom_property):
        cls.custom_properties_defs[custom_property.name] = custom_property


class Edge: