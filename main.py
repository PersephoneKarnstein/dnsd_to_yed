import pandas as pd
import pyyed, urllib, warnings, math
from matplotlib import cm #for colorization of arbitrary numbers of lines

global g
g = pyyed.Graph()

################################################################################
# remove all non-alphanumeric characters from a string (including spaces), for 
# non-glitchy naming of nodes and properties

def wanted(character):
    # create a mask
    return character.isalnum()

ascii_characters = [chr(ordinal) for ordinal in range(128)]
ascii_code_point_filter = [c if wanted(c) else None for c in ascii_characters]
# mask the list of ascii characters by whether or not they match the 
# criteria set in wanted()

def fast_clean(string):
    # Remove all non-ASCII characters. Heavily optimised.
    string = string.encode('ascii', errors='ignore').decode('ascii')

    # Remove unwanted ASCII characters
    return string.translate(ascii_code_point_filter)
################################################################################


def defineProps(theFile):
    ################################################################################
    # define custom properties for the Node class so that it can carry all the information
    # included in the dnsdumpster file, i.e. ["Hostname", "IP Address", "Type", "Reverse \
    # DNS", "Netblock Owner", "Country", "Tech / Apps", "HTTP / Title", "HTTPS / Title", \
    # "FTP / SSH / Telnet", # "HTTP Other"]

    propertyNames = theFile.columns.to_list()
    for propertyName in propertyNames:
        safername = fast_clean(propertyName)
        g.define_custom_property("node", safername, "string", "")

    g.define_custom_property("node", "textColor", "string", "#000000")
    ################################################################################

def lineColor(dnsrecordtype, _knownTypes = ["A", "AAAA", "AFSDB", "APL", "CAA", "CDNSKEY", "CDS", "CERT", "CNAME", "CSYNC", \
        "DHCID", "DLV", "DNAME", "DNSKEY", "DS", "EUI48", "EUI64", "HINFO", "HIP", "IPSECKEY", "KEY", \
            "KX", "LOC", "MX", "NAPTR", "NS", "NSEC", "NSEC3", "NSEC3PARAM", "OPENPGPKEY", "PTR", "RRSIG", \
                "RP", "SIG", "SMIMEA", "SOA", "SRV", "SSHFP", "TA", "TKEY", "TLSA", "TSIG", "TXT", "URI", \
                    "ZONEMD", "SVCB", "HTTPS"]):
    
    if type(dnsrecordtype) != str:
        raise ValueError(f'The given record type ("{dnsrecordtype}") should be a string.')

    cmap = cm.get_cmap('gist_rainbow')

    dnsrecordtype = fast_clean(dnsrecordtype.strip()).upper()
    if dnsrecordtype not in _knownTypes:
        warnings.warn(f"{dnsrecordtype} is not a known DNS record type. This may indicate a misconfigured xlsx read.", \
            RuntimeWarning)
        colorTuple = cmap(abs(hash(dnsrecordtype))/(10**(1+int(math.log10(abs(hash(dnsrecordtype)))))))
        #ugly but will consistently return the same color for the same input

    else:
        colorTuple = cmap(_knownTypes.index(dnsrecordtype)/len(_knownTypes))

    colorTuple = tuple([round(255*x) for x in colorTuple][:-1])
    color = "#{:02x}{:02x}{:02x}".format(*colorTuple).upper()
    return color 

def __main__(theFile, g=g, savename=None):
    
    defineProps(theFile)

    # add a base node for all the records to attach to
    baseNodeName = ".".join(theFile["Hostname"].get(0).split(".")[:-1])

    if savename is None:
        savename = baseNodeName+".graphml"
    elif savename.split('.')[-1] == "graphml":
        savename = savename
    else:
        savename = savename+".graphml"
    print("saving as "+savename)

    baseNode = g.add_node("baseNode", label=baseNodeName,\
        label_alignment="center", shape="roundrectangle", font_family="Courier",\
            underlined_text="false", font_style="bold", font_size="14",\
                shape_fill="#226f6d", transparent="false", border_color="#aacccb",\
                    border_type="line", border_width="5.0", custom_properties={"textColor":"#aacccb"})


    ################################################################################
    # to mimic how DNSDumpster formats their online graph viewer (beta), create 
    # nodes to sort by record type, and then group the child records by netblock owner

    recordTypes = set(theFile["Type"].to_list()) #Get the unique DNS record types
    for recordType in recordTypes:
        #don't need to clean because they can only be a small set of already-compliant names
        nodename = "recordType"+recordType.strip()
        globals()[nodename] = g.add_node(nodename, label=recordType,\
            shape="ellipse", font_family="Arial", underlined_text="false",\
                font_style="bold", font_size="12", shape_fill="#000000",\
                    transparent="false", border_color="#000000", border_type="line",\
                        custom_properties={"textColor":"#FFFFFF"})

        g.add_edge("baseNode", nodename, description="Record Type", arrowhead="none", color=lineColor(recordType, list(recordTypes)))

    #Get the unique netblock owners, and create a group for each
    netblockOwners = set(theFile["Netblock Owner"].to_list()) 
    for netblockOwner in netblockOwners:
        groupName = "netblockOwner"+fast_clean(netblockOwner)
        globals()[groupName] = g.add_group(groupName, label=netblockOwner,\
            label_alignment="center", shape="roundrectangle", \
                closed="false", font_family="Courier", underlined_text="false", \
                    font_style="plain", font_size="14", fill="#B4B4B4", transparent="true", \
                        border_color="#000000", border_type="line", border_width="2.0")#custom_properties={"textColor":"#FFFFFF"}
        
        #mask the dataframe to only show records owned by this netblock owner
        discriminator = theFile["Netblock Owner"] == netblockOwner
        nodesOwned = theFile[discriminator] 

        # for each record in the mask, set each of the custom defined properties
        # to the value dnsdumpster reported
        for recordTuple in nodesOwned.iterrows():
            record = recordTuple[1]
            customProperties = dict()
            propertyNames = theFile.columns.to_list()
            for propertyName in propertyNames:
                safername = fast_clean(propertyName)
                # dnsdumpster xlsx file records a null response as NaN, but we told
                # graphml to expect strings, so quickly clean that
                if type(record[propertyName])==str: 
                    customProperties[safername] = record[propertyName]
                else: customProperties[safername] = ""
                    
            nodename = "recordFor"+ fast_clean(str(record["Hostname"]))
            recordtype = "recordType"+str(record["Type"]).strip()
            

            try: globals()[groupName].add_node(\
                nodename,\
                    label=str(record["IP Address"])+"\n"+str(record["Hostname"]),\
                        label_alignment="center", shape="rectangle", font_family="Arial",\
                            underlined_text="false", font_style="plain", font_size="12",\
                                shape_fill="#b4b4b4", transparent="false", border_color="#494949",\
                                    border_type="line", border_width="5.0", custom_properties=customProperties.update({"textColor":"#494949"}))
            except RuntimeWarning: pass

            g.add_edge(recordtype, nodename,\
                label=str(record["Reverse DNS"]), description="Reverse DNS",\
                    color=lineColor(str(record["Type"]), list(recordTypes))\
                        )
    ################################################################################

    # and save
    g.write_graph(savename, pretty_print=True)