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
    {"id":"dummy","lat":12,"lon":56,"tags":{}}  ]
    }
    <!-- XSLT til at udtrække restauranter fra http://www.findsmiley.dk/xml/allekontrolresultater.xml og generere JSON -->
    <!-- Niels Elgaard Larsen elgaard@agol.dk -->
    <!-- GPL3 -->
  </xsl:template>


  <xsl:template match="Geo_Lng[not(node())]">
    -0.44
  </xsl:template>
  
  <xsl:template match="/document/row">
    <xsl:if test="not (brancheKode='99.99.99.H')">
      <xsl:if test="not (contains(navn1,'Ophørt '))">

	<xsl:if test="seneste_kontrol!=''">
	    {
	    "id":<xsl:value-of select="navnelbnr"/>,    
	    "lat":<xsl:choose><xsl:when test="Geo_Lat !=''">
            <xsl:value-of select="Geo_Lat"/>
            </xsl:when> <xsl:otherwise>0.000</xsl:otherwise>
            </xsl:choose>,
	    "lon":<xsl:choose>
            <xsl:when test="Geo_Lng !=''">
              <xsl:value-of select="Geo_Lng"/>
              </xsl:when> <xsl:otherwise>0.0</xsl:otherwise>
            </xsl:choose>,
	    "city":"<xsl:value-of select="By"/>",
	    "tags": {
	    "amenity":"restaurant",
	    "name":"<xsl:value-of select="translate(normalize-space(navn1),'&quot;','')"/>"
	    }
	    },
	  </xsl:if>
        </xsl:if>
      </xsl:if>
  </xsl:template>
</xsl:stylesheet>


<!-- genererer et ekstra komma, som man kan fjerne manuelt -->

