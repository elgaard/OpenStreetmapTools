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

    <!-- todo Branche: 56.10.00.C Servering: Restauranter mv. - åbent op til 6 måneder om året
         Branche: 56.10.00.A Servering: Restauranter mv
    -->
    
  </xsl:template>
  <xsl:template match="row">
    <xsl:if test="@pixibranche='Restauranter, pizzeriaer, kantiner m.m.' or @brancheKode='56.10.00.B'">
      <xsl:if test="not (@brancheKode='99.99.99.H')">
	<xsl:if test="@virksomhedstype='Detail'">
	  <xsl:if test="@brancheKode!='56.29.00.A'"> <!-- Servering: Kantiner mv., fast personkreds over 12 personer -->
	    <xsl:if test="@Geo_Lat!=''">
	      <xsl:if test="not (contains(@navn1,'Ophørt ') or contains(@navn1,' mobile')  or contains(@navn1,'Mobile')  or contains(@navn1,'Brugsen')  or contains(@navn1,'Psykia')  or contains(@navn1,'PSYKIA')  or contains(@navn1,'Truck') or contains(@navn1,'Texaco')  or contains(@navn1,'Kommune') or contains(@navn1,' afsnit')  or contains(@navn1,'Afsnit') or contains(@navn1,'Kursus') or contains(@navn1,' vogn') or contains(@navn1,'Shell') or contains(@navn1,'Lager') or contains(@navn1,'Kantine') or contains(@navn1,'Pølsevogn') or contains(@navn1,'Butik') or contains(@navn1,'Catering') or contains(@navn1,'hjemmet') or contains(@navn1,'klubben') or contains(@navn1,'MENY') or contains(@navn1,'Statoil ') or contains(@navn1,'CIRCLE K') or contains(@navn1,'Circle K') or contains(@navn1,'Vognen') or contains(@navn1,'Vogn ') or contains(@navn1,'hallen') or contains(@navn1,'vognen')  or contains(@navn1,'Produktionskøkken') or contains(@navn1,'Q8') or contains(@navn1,'køkkenet') or contains(@navn1,'OK ') or contains(@navn1,'Anretterkøkken') or contains(@navn1,' Candy') or contains(@navn1,'7-Eleven') or contains(@navn1,'Afd.') or contains(@navn1,'kantine') or contains(@navn1,'medicinsk') or contains(@navn1,'Sygehus') or contains(@navn1,'Afdeling') or contains(@navn1,'hospital') or contains(@navn1,'Hospital') or contains(@navn1,'afdeling') or contains(@navn1,'centret') or contains(@navn1,'center') or contains(@navn1,'Aktivitet') or contains(@navn1,'Bofælles') or contains(@navn1,'institution')or contains(@navn1,'Institution') or contains(@navn1,'lejehjem') or contains(@navn1,'Skole')or contains(@navn1,'skole') or contains(@navn1,'Fazer') or contains(@navn1,'Onkologisk') or contains(@navn1,'Driftsenhed') or contains(@navn1,'Danhostel') or contains(@navn1,'EUC') or contains(@navn1,'styrelsen') or contains(@navn1,'Psykiatrisk') or contains(@navn1,'elskab') or contains(@navn1,'orsamlings') or contains(@navn1,'kirurg') or contains(@navn1,'INSTITUTION'))">
		{
		"id":<xsl:value-of select="@navnelbnr"/>,    
		"lat":<xsl:value-of select="@Geo_Lat"/>,
		"lon":<xsl:value-of select="@Geo_Lng"/>,
		"city":"<xsl:value-of select="@By"/>",
		"branchekode":"<xsl:value-of select="@brancheKode"/>",
		"tags": {
		"amenity":"restaurant",
		"name":"<xsl:value-of select="translate(normalize-space(@navn1),'&quot;','')"/>"
		}
		},
	      </xsl:if>
	    </xsl:if>
	  </xsl:if>
	</xsl:if>
      </xsl:if>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>


<!-- genererer et ekstra komma, som man kan fjerne manuelt -->

