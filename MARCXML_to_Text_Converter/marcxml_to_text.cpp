#include <string>
#include <vector>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <list>

#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>

#include <xercesc/dom/DOM.hpp>
#include <xercesc/dom/DOMDocument.hpp>
#include <xercesc/dom/DOMDocumentType.hpp>
#include <xercesc/dom/DOMElement.hpp>
#include <xercesc/dom/DOMImplementation.hpp>
#include <xercesc/dom/DOMImplementationLS.hpp>
#include <xercesc/dom/DOMNodeIterator.hpp>
#include <xercesc/dom/DOMNodeList.hpp>
#include <xercesc/dom/DOMText.hpp>
#include <xercesc/dom/DOMNode.hpp>
#include <xercesc/dom/DOMNamedNodeMap.hpp>
#include <xercesc/framework/MemBufInputSource.hpp>
#include <xercesc/parsers/XercesDOMParser.hpp>
#include <xercesc/util/XMLUni.hpp>


using namespace xercesc;
using namespace std;

bool display_it(const XMLCh* tag, vector<string> tag_list){
   unsigned int i;
   unsigned int j;
   bool found_it=false;
   char* tag_char;
   std::string tag_str;
   if (tag_list.size() == 0){
          found_it=true;
          return found_it;
   }
   tag_char=XMLString::transcode(tag);
   tag_str=string(tag_char);
   // std::cerr << tag_str << std::endl;
   for (i=0; i < tag_list.size(); i++){
       if (tag_str.compare(tag_list[i]) == 0){
          found_it=true;
          break;
       }
   }
   XMLString::release(&tag_char);
   return found_it;
}

int process_marc_field(DOMNodeList* marc_field, vector<string> tag_list)
{
  int outcome;
  XMLSize_t field_count;
  int n_type;
  int idx;
  XMLSize_t count;
  XMLSize_t nodeCount;
  XMLSize_t elementCount;
  DOMNode::NodeType node_type;
  DOMNodeList* children;
  outcome=0;
  const XMLCh*  tagName; 
  char*  text_display; 
  char*  attr_display; 
  const XMLCh*  leader; 
  const XMLCh*  control_field; 
  const XMLCh*  attribute; 
  const XMLCh*  text; 
  std::string  subfield_text=""; 
  const XMLCh* indicator1;
  const XMLCh* indicator2;
  std::string  datafield;
  bool list_all=false;
  char*  tag_char;
  std::string  tag_str;
  DOMNamedNodeMap *attribute_list;
  const XMLCh* ZEROS=XMLString::transcode("000");
  const XMLCh* TAG=XMLString::transcode("tag");
  const XMLCh* CODE=XMLString::transcode("code");
  const XMLCh* INDICATOR1=XMLString::transcode("ind1");
  const XMLCh* INDICATOR2=XMLString::transcode("ind2");
  const XMLCh* LEADER=XMLString::transcode("leader");
  const XMLCh* CONTROLFIELD=XMLString::transcode("controlfield");
  const XMLCh* DATAFIELD=XMLString::transcode("datafield");
  XMLCh* subfieldText;
  if (tag_list.size() == 0){
     list_all=true;
  }
  field_count = marc_field->getLength();
  std::string  wide_char="下一条记录";  // practicing my chinese!
  std::cerr <<  wide_char << std::endl;
  std::cout << "*******" << std::endl;
  for( XMLSize_t xx = 0; xx < field_count; ++xx ){
     DOMNode* currentNode = marc_field->item(xx);
     node_type=currentNode->getNodeType();
     n_type=int(node_type);
     //std::cerr << "node_type: " << n_type  << " " << DOMNode::ELEMENT_NODE << std::endl;

     if( currentNode->getNodeType() &&  // true is not NULL
            currentNode->getNodeType() == DOMNode::ELEMENT_NODE ) // is element
     {
            // Found node which is an Element. Re-cast node as element
           DOMElement* currentElement = dynamic_cast< xercesc::DOMElement* >( currentNode );
          tagName = currentElement->getTagName();
          if (XMLString::equals(tagName,LEADER)){
             leader=currentElement->getTextContent();
             text_display=XMLString::transcode(leader);
             if (display_it(ZEROS,tag_list)){
                std::cout << "000||" << text_display << std::endl;
             }
             XMLString::release(&text_display);
          }
          else if (XMLString::equals(tagName,CONTROLFIELD)){
             control_field=currentElement->getTextContent();
//             std::cerr << "found controlfield " <<  control_field << std::endl;
             attribute=currentElement->getAttribute(TAG);
             //std::cerr << "controlfield " << attribute << " " << control_field  <<  std::endl;
             text_display=XMLString::transcode(control_field);
             attr_display=XMLString::transcode(attribute);
             if (display_it(attribute,tag_list)){
                 std::cout << attr_display << "||" << text_display  <<  std::endl;
             }
             XMLString::release(&text_display);
             XMLString::release(&attr_display);
          }
          else if (XMLString::equals(tagName,DATAFIELD)){
             attribute_list=currentElement->getAttributes();
             attribute=currentElement->getAttribute(TAG);
             if (!display_it(attribute,tag_list)){
                 continue;
             }
             indicator1=currentElement->getAttribute(INDICATOR1);
             indicator2=currentElement->getAttribute(INDICATOR2);
             datafield="";
             text_display=XMLString::transcode(attribute);
             datafield.append(text_display);
             datafield.append("|");
             XMLString::release(&text_display);
             text_display=XMLString::transcode(indicator1);
             datafield.append(text_display);
             XMLString::release(&text_display);
             text_display=XMLString::transcode(indicator2);
             datafield.append(text_display);
             XMLString::release(&text_display);
             datafield.append("|");
             //std::cerr << "datafield tag " << attribute  << " " << indicator1 << " " << indicator2 <<  std::endl;
             //datafield="|"+indicator1+indicator2+"|";
             //std::cout << attribute << "|"  << indicator1 << indicator2 << "|" <<  std::endl;
       //    text=XMLString::transcode(currentElement->getTextContent());
       //    std::cerr << "datafield tag " << attribute  <<  " " << text << std::endl;
             children=currentElement->getChildNodes();
             elementCount = children->getLength();
             subfield_text="";
             subfieldText=XMLString::transcode("");
             for( XMLSize_t yy = 0; yy < elementCount; ++yy ){
                idx= int(yy);
                DOMNode* thisNode = children->item(yy);
                node_type=thisNode->getNodeType();
                n_type=int(node_type);
                //std::cerr << " subfield node_type: " << n_type  << " " << DOMNode::ELEMENT_NODE << std::endl; 

                if( thisNode->getNodeType() &&  // true is not NULL
                thisNode->getNodeType() == DOMNode::ELEMENT_NODE ) // is element 
                {
            // Found node which is an Element. Re-cast node as element
                   DOMElement* thisElement = dynamic_cast< xercesc::DOMElement* >( thisNode );
                   attribute=thisElement->getAttribute(CODE);
                   text=thisElement->getTextContent();
                   //std::cerr << "subfield code "  << attribute << " " << text << std::endl;
                   text_display=XMLString::transcode(attribute);
                   subfield_text.append("\\p"); // attribute+text;
                   subfield_text.append(text_display); // attribute+text;
                   XMLString::release(&text_display);
                   text_display=XMLString::transcode(text);
                   subfield_text.append(text_display); // attribute+text;
                   XMLString::release(&text_display);
                   //std::cout<<  datafield << "\\p"  << attribute << text << std::endl;
                }
             }
             std::cout<<  datafield << subfield_text << std::endl;
          }
          //XMLString::release(ptr);
 //         std::cerr << tag_name << std::endl;
     } // ELEMENT_NODE

  }
  return outcome;
}

int main(int argc, char* argv[])
{

    enum {
      ERROR_ARGS = 1,
      ERROR_XERCES_INIT,
      ERROR_PARSE,
      ERROR_EMPTY_DOCUMENT
    };


    xercesc::XercesDOMParser *m_ConfigFileParser;

    char* e_list;
    e_list=NULL;
    int done=0;
    int c;

    while ((c = getopt(argc, argv, "he:")) != -1) {
        switch(c) {
                case '?':
         std::cerr << "Usage: cat marcxml_file | " << argv[0] << " [-e tag1,tag2,...]" <<  std::endl;
         std::cerr << "valid marcxml format: <?xml version=\"1.0\" encoding=\"UTF-8\"?><collection><record></record></collection> " <<  std::endl;
         return 1;
                break;
                case 'e':
                        e_list=optarg;
                break;
                case 'h':
         std::cerr << "Usage: cat marcxml_file | " << argv[0] << " [-e tag1,tag2,...]" <<  std::endl;
         std::cerr << "valid marcxml format: <?xml version=\"1.0\" encoding=\"UTF-8\"?><collection><record></record></collection> " <<  std::endl;
         return 1;
                break;
        }
    }
  std::string args;
  vector<string> tag_list;
  if (e_list == NULL){
     tag_list.clear();
   }
   else{
     args=string(e_list);
     stringstream ss;
     ss << args;
     while( ss.good() )
     {
        string token;
        getline( ss, token, ',' );
        tag_list.push_back(token);
     }
   }

  std::string line="";
  std::string buffer="";
  std::string endofline="\n";
  std::string nothing="";
  while (std::getline(std::cin, line))
  {
    buffer+=line;
  }
  std::size_t found = buffer.rfind(endofline);
  if (found!=std::string::npos)  {
     buffer.replace (found,nothing.length(),nothing);

  }
  // std::cout << buffer << std::endl;
   try
   {
      XMLPlatformUtils::Initialize();  // Initialize Xerces infrastructure
   }
   catch( XMLException& e )
   {
      char* message = XMLString::transcode( e.getMessage() );
      cerr << "XML toolkit initialization error: " << message << endl;
      XMLString::release( &message );
      // throw exception here to return ERROR_XERCES_INIT
   }


   m_ConfigFileParser = new XercesDOMParser;
   m_ConfigFileParser->setValidationScheme( XercesDOMParser::Val_Never );
   m_ConfigFileParser->setDoNamespaces( false );
   m_ConfigFileParser->setDoSchema( false );
   m_ConfigFileParser->setLoadExternalDTD( false );

   try
   {
      MemBufInputSource input_source((XMLByte*)buffer.c_str(), strlen(buffer.c_str()), "bufId");
      m_ConfigFileParser->parse( input_source);
       DOMDocument* xmlDoc = m_ConfigFileParser->getDocument();

      DOMElement* elementRoot = xmlDoc->getDocumentElement();
      DOMNodeList* marc_field;
      XMLSize_t field_count;
        if( !elementRoot ) {
            std::cerr << " empty XML document. exiting" << std::endl;
            return 1;
         }
     
      DOMNodeList* children = elementRoot->getChildNodes();
      const  XMLSize_t nodeCount = children->getLength();
      int node_count=int(nodeCount);
      int idx;
      int n_type;
      DOMNode::NodeType node_type;
      DOMNamedNodeMap *attributes;
      XMLSize_t attr_count;
      int outcome;
      for( XMLSize_t xx = 0; xx < nodeCount; ++xx ){
         idx= int(xx);
          DOMNode* currentNode = children->item(xx);
          node_type=currentNode->getNodeType();
          n_type=int(node_type);

         if( currentNode->getNodeType() &&  // true is not NULL
            currentNode->getNodeType() == DOMNode::ELEMENT_NODE ) // is element 
         {
            // Found node which is an Element. Re-cast node as element
           DOMElement* currentElement = dynamic_cast< xercesc::DOMElement* >( currentNode );
           attributes=currentElement->getAttributes();
           attr_count=attributes->getLength();
           marc_field=currentElement->getChildNodes();
           outcome=process_marc_field(marc_field,tag_list);
         }
      }
   }
   catch( xercesc::XMLException& e )
   {
      char* message = xercesc::XMLString::transcode( e.getMessage() );
      ostringstream errBuf;
      errBuf << "Error parsing file: " << message << flush;
      XMLString::release( &message );
   }

   xercesc::XMLPlatformUtils::Terminate();
    return 0;
 
}
