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
<xsl:template match="row">
  <xsl:if test="@pixibranche='Restauranter, pizzeriaer, kantiner m.m.'">
    <xsl:if test="@virksomhedstype='Detail'">
      <xsl:if test="@Geo_Lat!=''">
	<xsl:if test="not (contains(@navn1,'Ophørt ') or contains(@navn1,'Kantine') or contains(@navn1,'Afd.') or contains(@navn1,'kantine') or contains(@navn1,'medicinsk') or contains(@navn1,'Sygehus') or contains(@navn1,'Afdeling') or contains(@navn1,'hospital') or contains(@navn1,'Hospital') or contains(@navn1,'afdeling') or contains(@navn1,'centret') or contains(@navn1,'center') or contains(@navn1,'Aktivitet') or contains(@navn1,'Bofælles') or contains(@navn1,'institution')or contains(@navn1,'Institution') or contains(@navn1,'lejehjem') or contains(@navn1,'Skole')or contains(@navn1,'skole') or contains(@navn1,'Fazer') or contains(@navn1,'Onkologisk') or contains(@navn1,'Driftsenhed') or contains(@navn1,'Danhostel') or contains(@navn1,'EUC') or contains(@navn1,'styrelsen') or contains(@navn1,'Psykiatrisk') or contains(@navn1,'elskab') or contains(@navn1,'orsamlings') or contains(@navn1,'kirurg') or contains(@navn1,'INSTITUTION'))">
	  {
          "id":<xsl:value-of select="@navnelbnr"/>,    
	  "lat":<xsl:value-of select="@Geo_Lat"/>,
	  "lon":<xsl:value-of select="@Geo_Lng"/>,
	  "city":"<xsl:value-of select="@By"/>",
	  "tags": {
	    "amenity":"restaurant",
	    "name":"<xsl:value-of select="translate(normalize-space(@navn1),'&quot;','')"/>"
	  }
	  },
	</xsl:if>
      </xsl:if>
    </xsl:if>
  </xsl:if>
</xsl:template>
</xsl:stylesheet>


<!-- genererer et ekstra komma, som man kan fjerne manuelt -->

