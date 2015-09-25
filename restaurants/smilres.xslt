<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.1"
    xmlns:fn="http://www.w3.org/2005/xpath-functions"
    >

<xsl:output method="text" encoding="utf-8"/>
<xsl:strip-space  elements="*"/>
    
<xsl:template match="/">
{
  "elements": [ 
    <xsl:apply-templates/>
null  ]
}
<!-- XSLT til at udtrække restauranter fra http://www.findsmiley.dk/xml/allekontrolresultater.xml og generere JSON -->
<!-- Niels Elgaard Larsen elgaard@agol.dk -->
<!-- GPL3 -->

</xsl:template>
<xsl:template match="row">
  <xsl:if test="@pixibranche='Restauranter, pizzeriaer, kantiner m.m.'">
    <xsl:if test="@Geo_Lat!=''">
      {
        "id":<xsl:value-of select="@navnelbnr"/>,    
	"lat":<xsl:value-of select="@Geo_Lat"/>,
	"lon":<xsl:value-of select="@Geo_Lng"/>,
	"tags": {
	"amenity":"restaurant",
	"name":"<xsl:value-of select="translate(normalize-space(@navn1),'&quot;','')"/>"
	}
      },
    </xsl:if>
  </xsl:if>
</xsl:template>
</xsl:stylesheet>


