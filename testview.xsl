<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    >

    <xsl:output method="html"/>

    <xsl:template match="/">
<!--header-->
<html><head><title>test.xml selection</title>
<link rel="stylesheet" href="static/jquery-ui.css" />
<link rel="stylesheet" href="static/testprep.css" />
<script src="static/jquery-1.9.1.js"></script>
<script src="static/jquery-ui.js"></script>
<script src="static/testprep-vertical-tabs.js" />
<script type="text/javascript">
    $(document).ready(function ($) {
        $('.explanation').hide();
        $('.answer').hide();
        var record = [];
        record.push({
            startview: Date.now(),
        })
        $('.showExplanation').click(function () {
            $('.explanation').hide();
            $(this).siblings('.explanation').show();
            $(this).siblings().children('.explanation').show();
            record.push({
                showanswer: Date.now(),
            })
            console.log(record);
            });
        $('.selectah').click(function () {
            $(this).siblings('.answer').addClass('explanation');
            record.push({
                question: $(this).attr('name'),
                response: $(this).attr('id'),
                datetime: Date.now(),
            });
        });
        $('.sendRecord').click(function () {
            record.push({
                sent: Date.now(),
            });
            console.log(record);
            $.ajax({
                type: "POST",
                url: "send",
                data: JSON.stringify(record)
            });
        });
    });
</script>
        </head>
        <body>
        <xsl:apply-templates select="qbank" />
        <!--footer-->
        </body></html>
    </xsl:template>

    <xsl:template match="qbank">
    <div id="tabs">
        <ul>
            <xsl:for-each select="question[@id]">
                <li><a href="#{@id}"><xsl:value-of select="@id" /></a></li>
            </xsl:for-each>
        </ul>

        <button class="sendRecord">send record</button>
        <br />

        <xsl:apply-templates select="question" />

    </div>
    </xsl:template>

    <xsl:template match="question">
        <div id="{@id}">
            <h2>Question <xsl:value-of select="@id" /></h2>
            <xsl:apply-templates select="prompt" />
            <xsl:apply-templates select="answerList" />
            <xsl:apply-templates select="explanation" />
        </div>
    </xsl:template>

    <xsl:template match="prompt">
        <xsl:apply-templates select="text()" />
    </xsl:template>
    
    <xsl:template match="answerList">
        <br />
        <xsl:apply-templates select="answer" />
        <button class="showExplanation">show answer</button>
    </xsl:template>

    <xsl:template match="answer">
        <div>
        <xsl:element name="input">
            <xsl:attribute name="type">radio</xsl:attribute>
            <xsl:attribute name="name">
                <xsl:value-of select="../../@id"/>
            </xsl:attribute>
            <xsl:attribute name="id">
                <xsl:value-of select="@id"/>
            </xsl:attribute>
            <xsl:attribute name="class">selectah</xsl:attribute>
        </xsl:element>
        <xsl:value-of select="." disable-output-escaping="yes"/>
        <xsl:element name="img">
            <xsl:attribute name="src">
                <xsl:choose>
                    <xsl:when test="@correct = 'true'">static/right.png</xsl:when>
                    <xsl:otherwise>static/wrong.png</xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <xsl:attribute name="class">answer</xsl:attribute>
        </xsl:element>
        </div>
        <br />
    </xsl:template>

    <xsl:template match="explanation">
        <div class="explanation">
        <xsl:apply-templates select="text()" />
        <p>why i missed this question</p>
        </div>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:value-of select='.' disable-output-escaping="yes" />
    </xsl:template>

</xsl:stylesheet>
        
