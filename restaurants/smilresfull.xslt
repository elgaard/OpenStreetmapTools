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


  <!--  vin: 47.25.00
       dagligvar 47.11.00.B
          47.11.00.B
       bager 10.71.20
       apotek: 47.29.00.A
       hospital 56.10.00.G
       slagter 47.22.00.A
       fiskehandel 47.23.00
       ostehandel 47.29.00.E
       kantiner 56.29.00.A
       detail behandling 47.29.00.C
       engros 46.39.00.D
       engros 46.00.00.D 
       chokolade 47.24.00.A
       born 56.29.00.C
       mobile 47.81.00.B
       kantiner/bosteder 56.10.00.E
       transportvirksomheder 49.41.00.D
       Kontor 46.00.00.C
       Plast 46.00.00.C
       Kontorfisk 46.38.00.A
       Engros frugt 46.31.00
       engros agentur 46.17.90
       Brødfabrikker 10.71.10.A
       Kontorvirksomhed, animalske fødevarer undtagen fisk og fiskevarer 46.30.00.A
       Distributionsterminaler  52.10.00.C
       Hakket Kød 10.10.00.A
       Catering 56.21.00
       Mobile 47.81.00.A
       røgning fisk 10.20.20.C
       Engros Kaffe 82.92.00.A
       Engroshandel 46.39.00.C
       for skolebørn 56.29.00.E
       førskolebørn 56.29.00.D
       engros fisk 46.38.10.A
       fremstilling porcelæn 20.00.00.B
       pak Gront 00.00.04.B
       Lagre og lagerhoteller 52.10.00.J
       Automater og automatvirksomheder 47.99.00.B
       Krydderier, smagspræparater 10.84.00.A
       Fiskevarevirksomheder, kun røgning, gravning og saltning 10.20.20.C
       ForelÃ¸big: Engroshandel 00.00.03.H
       ransportvirksomhed, engros 49.41.00.B
       Engroshandel og oplagring, ikke specialiseret, letfordÃ¦rvelige fÃ¸devarer 46.39.00.B
       Virksomhed, foreløbig: Mobil        00.00.02.C
       Lagre: Kød og kødprodukter, lagerhoteller  46.32.00.C 
  -->
  
<xsl:template match="/document/row">
<xsl:if test="not (brancheKode='99.99.99.H' or brancheKode='46.32.00.C' or brancheKode='00.00.02.C' or brancheKode='46.39.00.B' or brancheKode='49.41.00.B' or brancheKode='00.00.03.H' or brancheKode='10.20.20.C' or brancheKode='10.84.00.A' or brancheKode='47.99.00.B' or brancheKode='52.10.00.J' or brancheKode='00.00.04.B'  or  brancheKode='20.00.00.B' or  brancheKode='46.38.10.A' or  brancheKode='56.29.00.D' or  brancheKode='56.29.00.E' or brancheKode='46.39.00.C' or brancheKode='82.92.00.A'  or brancheKode=' 10.20.20.C' or brancheKode='47.81.00.A' or brancheKode='56.21.00' or brancheKode='10.10.00.A' or brancheKode='52.10.00.C' or brancheKode='46.30.00.A' or brancheKode='10.71.10.A' or brancheKode='46.17.90' or brancheKode='46.31.00'  or brancheKode='46.38.00.A' or brancheKode='46.00.00.C' or brancheKode='49.41.00.D' or brancheKode='56.10.00.E' or brancheKode='47.81.00.B'  or brancheKode='56.29.00.C'  or brancheKode='46.00.00.D' or brancheKode='47.24.00.A' or brancheKode='46.39.00.D' or brancheKode='47.29.00.C' or brancheKode='56.29.00.Ax' or brancheKode='47.29.00.E' or brancheKode='47.23.00' or brancheKode='47.22.00.A' or brancheKode='56.10.00.G' or brancheKode='47.29.00.A' or brancheKode='10.71.20' or brancheKode='47.11.00.A' or brancheKode='47.11.00.B' or brancheKode='47.21.00.A' or brancheKode='47.25.00' or brancheKode='46.17.90 ' ) ">
<xsl:if test="not (contains(navn1,'Ophørt '))"><xsl:if test="seneste_kontrol!='xxx'">
{"id":<xsl:value-of select="navnelbnr"/>,"lat":<xsl:choose><xsl:when test="Geo_Lat !=''"><xsl:value-of select="Geo_Lat"/></xsl:when> <xsl:otherwise>0.000</xsl:otherwise></xsl:choose>,"lon":<xsl:choose><xsl:when test="Geo_Lng !=''"><xsl:value-of select="Geo_Lng"/></xsl:when> <xsl:otherwise>0.0</xsl:otherwise></xsl:choose>,"operator":"<xsl:value-of select="Kaedenavn"/>",
"city":"<xsl:value-of select="By"/>","addr":"<xsl:value-of select="adresse1"/>","postnr":"<xsl:value-of select="postnr"/>",
"cvr":"<xsl:value-of select="cvrnr"/>","pnr":"<xsl:value-of select="pnr"/>","vt":"<xsl:value-of select="virksomhedstype"/>","pixi":"<xsl:value-of select="Pixibranche"/>","senestekontrol":"<xsl:value-of select="seneste_kontrol_dato"/>","branchekode":"<xsl:value-of select="brancheKode"/>",
"tags": {"amenity":"restaurant","name":"<xsl:value-of select="translate(normalize-space(navn1),'&quot;','')"/>"}},</xsl:if>
</xsl:if>
</xsl:if>
</xsl:template>
</xsl:stylesheet>


<!-- genererer et ekstra komma, som man kan fjerne manuelt -->

