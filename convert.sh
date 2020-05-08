#!/bin/sh

IFS='
'


usage() {
    echo "usage: $0 aws_icon_dir target_dir"
    echo "example: ./convert.sh ~/Downloads/AWS-Architecture-Icons_EPS/Light-BG/ ./19.05.21"
}

create_stencil() {
    subdir="$1"
    mkdir "$OUTPUT_DIR/$subdir.gstencil"
    i=1
    images=""

    for eps in $(find "$AWS_DIR/$subdir" -name '*_light-bg.eps' | sort); do
        id=$(echo $eps | sed "s|^$AWS_DIR/||" | sed "s|_light-bg.eps$||")
        pdf="$OUTPUT_DIR/$subdir.gstencil/image$i.pdf"
        epstopdf "$eps" "$pdf"

        pdf_size=$(pdfinfo $pdf | perl -ne 'print if s/^Page size:\s+([\d]+) x ([\d]+).*/{\1, \2}/')
        name=$(cat meta.txt | perl -ne 'print if s|'$id': name: (.*)$|\1|')
        url=$(cat meta.txt | perl -ne 'print if s|'$id': url: (.*)$|\1|')

        if [ -z "$name" ]; then
            echo "WARNING: Missing meta for $id"
        fi

        images=$images'
                <dict>
                    <key>Bounds</key>
                    <string>{{0, 0}, '$pdf_size'}</string>
                    <key>Class</key>
                    <string>ShapedGraphic</string>
                    <key>ID</key>
                    <integer>'$(($i + 1))'</integer>
                    <key>ImageID</key>
                    <integer>'$i'</integer>
                    <key>Magnets</key>
                    <array>
                        <string>{1, 1}</string>
                        <string>{1, -1}</string>
                        <string>{-1, -1}</string>
                        <string>{-1, 1}</string>
                        <string>{0, 1}</string>
                        <string>{0, -1}</string>
                        <string>{1, 0}</string>
                        <string>{-1, 0}</string>
                    </array>
                    <key>Name</key>
                    <string>'$name'</string>
                    <key>Notes</key>
                    <string>{\\rtf1\\ansi\\ansicpg1252\\cocoartf1561\\cocoasubrtf600
{\\fonttbl\\f0\\fswiss\\fcharset0 Helvetica;}
{\\colortbl;\\red255\\green255\\blue255;}
{\\*\\expandedcolortbl;;}
\\pard\\tx560\\tx1120\\tx1680\\tx2240\\tx2800\\tx3360\\tx3920\\tx4480\\tx5040\\tx5600\\tx6160\\tx6720\\pardirnatural\\partightenfactor0

\\f0\\fs24 \\cf0 '$url'}</string>
                    <key>Style</key>
                    <dict>
                        <key>fill</key>
                        <dict>
                            <key>Draws</key>
                            <string>NO</string>
                        </dict>
                        <key>shadow</key>
                        <dict>
                            <key>Draws</key>
                            <string>NO</string>
                        </dict>
                        <key>stroke</key>
                        <dict>
                            <key>Draws</key>
                            <string>NO</string>
                        </dict>
                    </dict>
                </dict>'

        i=$(($i+1))
    done

    image_count=$(($i-1))

    echo "Stencil item count: $image_count"

    dict_1=""
    for i in $(seq 1 $image_count); do
        dict_1="$dict_1\n        <dict/>"
    done

    string_1=""
    for i in $(seq 1 $image_count); do
        string_1="$string_1\n        <string>image$i.pdf</string>"
    done


    echo '<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>ApplicationVersion</key>
    <array>
        <string>com.omnigroup.OmniGraffle7.MacAppStore</string>
        <string>192.21</string>
    </array>
    <key>GraphDocumentVersion</key>
    <integer>16</integer>
    <key>GuidesLocked</key>
    <string>NO</string>
    <key>GuidesVisible</key>
    <string>YES</string>
    <key>ImageCounter</key>
    <integer>'$(($image_count+1))'</integer>
    <key>ImageLinkBack</key>
    <array>'$dict_1'
    </array>
    <key>ImageList</key>
    <array>'$string_1'
    </array>
    <key>LinksVisible</key>
    <string>NO</string>
    <key>MagnetsVisible</key>
    <string>NO</string>
    <key>MasterSheets</key>
    <array/>
    <key>ModificationDate</key>
    <string>2019-03-04 17:39:27 +0000</string>
    <key>Modifier</key>
    <string>Smith, David</string>
    <key>MovementHandleVisible</key>
    <string>NO</string>
    <key>NotesVisible</key>
    <string>NO</string>
    <key>OriginVisible</key>
    <string>NO</string>
    <key>PageBreaks</key>
    <string>NO</string>
    <key>PrintInfo</key>
    <dict>
        <key>NSBottomMargin</key>
        <array>
            <string>float</string>
            <string>40</string>
        </array>
        <key>NSHorizonalPagination</key>
        <array>
            <string>coded</string>
            <string>BAtzdHJlYW10eXBlZIHoA4QBQISEhAhOU051bWJlcgCEhAdOU1ZhbHVlAISECE5TT2JqZWN0AIWEASqEhAFxlwCG</string>
        </array>
        <key>NSLeftMargin</key>
        <array>
            <string>float</string>
            <string>18</string>
        </array>
        <key>NSPaperName</key>
        <array>
            <string>string</string>
            <string>na-letter</string>
        </array>
        <key>NSPaperSize</key>
        <array>
            <string>size</string>
            <string>{611.99997711181641, 792}</string>
        </array>
        <key>NSPrintReverseOrientation</key>
        <array>
            <string>coded</string>
            <string>BAtzdHJlYW10eXBlZIHoA4QBQISEhAhOU051bWJlcgCEhAdOU1ZhbHVlAISECE5TT2JqZWN0AIWEASqEhAFxlwCG</string>
        </array>
        <key>NSRightMargin</key>
        <array>
            <string>float</string>
            <string>18</string>
        </array>
        <key>NSTopMargin</key>
        <array>
            <string>float</string>
            <string>18</string>
        </array>
    </dict>
    <key>ReadOnly</key>
    <string>NO</string>
    <key>Sheets</key>
    <array>
        <dict>
            <key>ActiveLayerIndex</key>
            <integer>0</integer>
            <key>AutoAdjust</key>
            <integer>6</integer>
            <key>AutosizingMargin</key>
            <integer>1</integer>
            <key>BackgroundGraphic</key>
            <dict>
                <key>Bounds</key>
                <string>{{0, 0}, {1000, 1000}}</string>
                <key>Class</key>
                <string>GraffleShapes.CanvasBackgroundGraphic</string>
                <key>ID</key>
                <integer>0</integer>
                <key>Style</key>
                <dict>
                    <key>shadow</key>
                    <dict>
                        <key>Draws</key>
                        <string>NO</string>
                    </dict>
                    <key>stroke</key>
                    <dict>
                        <key>Draws</key>
                        <string>NO</string>
                    </dict>
                </dict>
            </dict>
            <key>BaseZoom</key>
            <integer>0</integer>
            <key>CanvasDimensionsOrigin</key>
            <string>{0, 0}</string>
            <key>CanvasOrigin</key>
            <string>{0, 0}</string>
            <key>CanvasSize</key>
            <string>{1000, 1000}</string>
            <key>CanvasSizingMode</key>
            <integer>1</integer>
            <key>ColumnAlign</key>
            <integer>0</integer>
            <key>ColumnSpacing</key>
            <real>36</real>
            <key>DisplayScale</key>
            <string>1.0 pt = 1.0 px</string>
            <key>GraphicsList</key>
            <array>'"$images"'
            </array>
            <key>GridInfo</key>
            <dict>
                <key>DrawMajorGrid</key>
                <string>NO</string>
                <key>GridSpacing</key>
                <real>1</real>
                <key>MajorGridSpacing</key>
                <integer>1</integer>
                <key>MinorGridColor</key>
                <dict>
                    <key>a</key>
                    <string>0.3</string>
                    <key>space</key>
                    <string>gg22</string>
                    <key>w</key>
                    <string>0.723367</string>
                </dict>
                <key>ShowsGrid</key>
                <string>YES</string>
                <key>SnapsToGrid</key>
                <string>YES</string>
            </dict>
            <key>HPages</key>
            <integer>5</integer>
            <key>KeepToScale</key>
            <false/>
            <key>Layers</key>
            <array>
                <dict>
                    <key>Artboards</key>
                    <false/>
                    <key>Lock</key>
                    <false/>
                    <key>Name</key>
                    <string>Layer 1</string>
                    <key>Print</key>
                    <true/>
                    <key>View</key>
                    <true/>
                </dict>
            </array>
            <key>LayoutInfo</key>
            <dict>
                <key>Animate</key>
                <string>NO</string>
                <key>circoMinDist</key>
                <real>18</real>
                <key>circoSeparation</key>
                <real>0.0</real>
                <key>layoutEngine</key>
                <string>dot</string>
                <key>neatoLineLength</key>
                <real>0.20000000298023224</real>
                <key>neatoSeparation</key>
                <real>0.0</real>
                <key>twopiSeparation</key>
                <real>0.0</real>
            </dict>
            <key>Orientation</key>
            <integer>2</integer>
            <key>PrintOnePage</key>
            <false/>
            <key>RowAlign</key>
            <integer>0</integer>
            <key>RowSpacing</key>
            <real>36</real>
            <key>SheetTitle</key>
            <string>Canvas 1</string>
            <key>UniqueID</key>
            <integer>1</integer>
            <key>VPages</key>
            <integer>1</integer>
            <key>VisibleVoidKey</key>
            <real>1</real>
        </dict>
    </array>
    <key>SmartAlignmentGuidesActive</key>
    <string>NO</string>
    <key>SmartDistanceGuidesActive</key>
    <string>NO</string>
    <key>UseEntirePage</key>
    <false/>
    <key>WindowInfo</key>
    <dict>
        <key>CurrentSheet</key>
        <integer>0</integer>
        <key>Frame</key>
        <string>{{-0, -0}, {1280, 1418}}</string>
        <key>ShowInfo</key>
        <true/>
        <key>Sidebar</key>
        <true/>
        <key>SidebarWidth</key>
        <integer>244</integer>
        <key>Sidebar_Tab</key>
        <integer>0</integer>
        <key>WindowInfo_InspectorTab</key>
        <array>
            <string>com.omnigroup.OmniGraffle.inspectorGroup.properties</string>
        </array>
        <key>ZoomValues</key>
        <array>
            <array>
                <string>Canvas 1</string>
                <real>1</real>
                <real>1</real>
            </array>
        </array>
    </dict>
    <key>compressOnDiskKey</key>
    <false/>
    <key>copyLinkedImagesKey</key>
    <false/>
    <key>createSinglePDFKey</key>
    <false/>
    <key>exportAreaKey</key>
    <integer>4</integer>
    <key>exportQualityKey</key>
    <real>100</real>
    <key>exportSizesKey</key>
    <array>
        <integer>1</integer>
        <string></string>
    </array>
    <key>fileFormatKey</key>
    <integer>0</integer>
    <key>htmlImageTypeKey</key>
    <integer>0</integer>
    <key>includeBackgroundGraphicKey</key>
    <true/>
    <key>includeNonPrintingLayersKey</key>
    <false/>
    <key>lastExportTypeKey</key>
    <integer>0</integer>
    <key>marginWidthKey</key>
    <real>9</real>
    <key>readOnlyKey</key>
    <false/>
    <key>resolutionForBMPKey</key>
    <real>1</real>
    <key>resolutionForGIFKey</key>
    <real>1</real>
    <key>resolutionForHTMLKey</key>
    <real>1</real>
    <key>resolutionForJPGKey</key>
    <real>1</real>
    <key>resolutionForPNGKey</key>
    <real>1</real>
    <key>resolutionForTIFFKey</key>
    <real>1</real>
    <key>resolutionUnitsKey</key>
    <integer>0</integer>
    <key>saveAsFlatFileOptionKey</key>
    <integer>1</integer>
    <key>useArtboardsKey</key>
    <true/>
    <key>useMarginKey</key>
    <false/>
    <key>useNotesKey</key>
    <true/>
</dict>
</plist>
' | gzip > "$OUTPUT_DIR/$subdir.gstencil/data.plist"
}

if ! [ $# -eq 2 ]; then
    usage
    exit 1
fi

AWS_DIR=$1
OUTPUT_DIR=$2

if ! which -s epstopdf; then
    echo "error: epstopdf not found. Install it with 'brew cask install mactex'"
    exit 1
fi

if ! which -s pdfinfo; then
    echo "error: pdfinfo not found. Install it with 'brew install xpdf'"
    exit 1
fi

if [ ! -f meta.txt ]; then
    echo "error: meta.txt not found. Please run the script from the same directory'"
    exit 1
fi

if ! [ -d "$AWS_DIR" ]; then
    echo "error: $AWS_DIR is not a directory"
    exit 1
fi

if ! [ -d "$OUTPUT_DIR" ]; then
    echo "creating $OUTPUT_DIR ..."
    if ! mkdir -p "$OUTPUT_DIR"; then
        echo "error: could not create $OUTPUT_DIR"
        exit 1
    fi
fi

echo "creating stencils in $OUTPUT_DIR ..."

for d in $(find $AWS_DIR -type d -maxdepth 1 -mindepth 1); do
    d_short=$(basename "$d")
    echo "Directory: $d_short"
    create_stencil "$d_short"
done
