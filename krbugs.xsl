<!--
    Niels Elgaard Larsen 2015
     XSLT script to convert Keepright GPX bugs to format suitable for GPS applications
-->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xmlns:g="http://www.topografix.com/GPX/1/1"    
    >
  <xsl:output indent="yes" method="xml"/>
  <xsl:template match="g:gpx">
    <gpx xmlns="http://www.topografix.com/GPX/1/1" creator="keeprightT" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
      <xsl:for-each select="//g:wpt">
	<wpt>
	<xsl:attribute name="lat"> <xsl:value-of select="@lat" /></xsl:attribute>
	<xsl:attribute name="lon"> <xsl:value-of select="@lon" /></xsl:attribute>
	  <name><xsl:value-of select="g:name"/>: <xsl:value-of select="g:desc"/></name>
	</wpt>
      </xsl:for-each>
    </gpx>
  </xsl:template>
</xsl:stylesheet>
