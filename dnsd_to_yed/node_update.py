class Group:
    def __init__(self, group_id, parent_graph, label=None, label_alignment="center", shape="rectangle",
                 closed="false", font_family="Dialog", underlined_text="false",
                 font_style="plain", font_size="12", font_color="#000000", fill="#FFCC00", fill2=None, transparent="false",
                 border_color="#000000", border_type="line", border_width="1.0", height=False,
                 width=False, x=False, y=False, description="", url=""):

        self.label = label
        if label is None:
            self.label = group_id

        self.parent = None
        self.group_id = group_id
        self.nodes = {}
        self.groups = {}
        self.parent_graph = parent_graph
        self.edges = {}
        self.num_edges = 0

        # node shape
        if shape not in node_shapes:
            raise RuntimeWarning("Node shape %s not recognised" % shape)
        self.shape = shape

        self.closed = closed

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

        self.fill = fill
        self.fill2 = fill2
        self.transparent = transparent

        self.geom = {}
        if height:
            self.geom["height"] = height
        if width:
            self.geom["width"] = width
        if x:
            self.geom["x"] = x
        if y:
            self.geom["y"] = y

        self.border_color = border_color
        self.border_width = border_width

        if border_type not in line_types:
            raise RuntimeWarning("Border type %s not recognised" % border_type)

        self.border_type = border_type

        self.description = description
        self.url = url

    def add_node(self, node_name, **kwargs):
        if node_name in self.parent_graph.existing_entities:
            raise RuntimeWarning("Node %s already exists" % node_name)

        node = Node(node_name, **kwargs)
        node.parent = self
        self.nodes[node_name] = node
        self.parent_graph.existing_entities[node_name] = node
        return node

    def add_group(self, group_id, **kwargs):
        if group_id in self.parent_graph.existing_entities:
            raise RuntimeWarning("Node %s already exists" % group_id)

        group = Group(group_id, self.parent_graph, **kwargs)
        group.parent = self
        self.groups[group_id] = group
        self.parent_graph.existing_entities[group_id] = group
        return group

    def is_ancestor(self, node):
        return node.parent is not None and (
            node.parent is self or self.is_ancestor(node.parent))

    def add_edge(self,  node1_name, node2_name, **kwargs):
        # pass node names, not actual node objects

        node1 = self.parent_graph.existing_entities.get(node1_name) or \
            self.add_node(node1_name)

        node2 = self.parent_graph.existing_entities.get(node2_name) or \
            self.add_node(node2_name)

        # http://graphml.graphdrawing.org/primer/graphml-primer.html#Nested
        # The edges between two nodes in a nested graph have to be declared in a graph,
        # which is an ancestor of both nodes in the hierarchy.

        if not (self.is_ancestor(node1) and self.is_ancestor(node2)):
            raise RuntimeWarning("Group %s is not ancestor of both %s and %s" % (self.group_id, node1_name, node2_name))

        self.parent_graph.num_edges += 1
        kwargs['edge_id'] = str(self.parent_graph.num_edges)
        edge = Edge(node1_name, node2_name, **kwargs)
        self.edges[edge.edge_id] = edge
        return edge

    def convert(self):
        node = ET.Element("node", id=self.group_id)
        node.set("yfiles.foldertype", "group")
        data = ET.SubElement(node, "data", key="data_node")

        # node for group
        pabn = ET.SubElement(data, "y:ProxyAutoBoundsNode")
        r = ET.SubElement(pabn, "y:Realizers", active="0")
        group_node = ET.SubElement(r, "y:GroupNode")

        if self.geom:
            ET.SubElement(group_node, "y:Geometry", **self.geom)

        if self.fill2:
            ET.SubElement(group_node, "y:Fill", color=self.fill, color2=self.fill2, transparent=self.transparent)
        else:
            ET.SubElement(group_node, "y:Fill", color=self.fill, transparent=self.transparent)

        ET.SubElement(group_node, "y:BorderStyle", color=self.border_color,
                      type=self.border_type, width=self.border_width)

        label = ET.SubElement(group_node, "y:NodeLabel", modelName="internal",
                              modelPosition="t",
                              fontFamily=self.font_family, fontSize=self.font_size,
                              underlinedText=self.underlined_text,
                              fontStyle=self.font_style,
                              alignment=self.label_alignment,
                              textColor=self.font_color)
        label.text = self.label

        ET.SubElement(group_node, "y:Shape", type=self.shape)

        ET.SubElement(group_node, "y:State", closed=self.closed)

        graph = ET.SubElement(node, "graph", edgedefault="directed", id=self.group_id)

        if self.url:
            url_node = ET.SubElement(node, "data", key="url_node")
            url_node.text = self.url

        if self.description:
            description_node = ET.SubElement(node, "data", key="description_node")
            description_node.text = self.description

        for node_id in self.nodes:
            n = self.nodes[node_id].convert()
            graph.append(n)

        for group_id in self.groups:
            n = self.groups[group_id].convert()
            graph.append(n)

        for edge_id in self.edges:
            e = self.edges[edge_id].convert()
            graph.append(e)

        return node
        # ProxyAutoBoundsNode crap just draws bar at top of group

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