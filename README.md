AWS-OmniGraffle-Stencils
========================

If use OmniGraffle and AWS - these stencils are for you.

OmniGraffle compatible versions of the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/).

## 26.04.30 Icons (latest)
Light background icons converted from the modern AWS **SVG** asset pack
(`Asset-Package_04302026`). Since the 2025/2026 refresh AWS no longer ships EPS —
the pack is SVG/PNG — so this set is built with a new converter, [convert.py](convert.py)
(see [Creating stencil files](#creating-stencil-files) below).

The icons are organised into sub-folders that mirror AWS's own structure, so the
stencils land in OmniGraffle as tidy groups:

| Folder | Stencils | What it is |
|---|---|---|
| `Architecture Service Icons/` | one per category (Analytics, Compute, …) | the main 64&nbsp;px service icons |
| `Resource Icons/` | one per category | the 48&nbsp;px resource icons |
| `Group Icons.gstencil` | 1 | VPC / Region / Account containers etc. |
| `Category Icons.gstencil` | 1 | the category badges |
| `AWS All Icons.gstencil` | 1 (optional) | **every** icon above in one stencil — handy for searching across all of AWS at once (built with `--combined`) |

## 20.04.30 Icons
Light background icons converted from [AWS-Architecture-Icons_EPS_20200430](https://d1.awsstatic.com/webteam/architecture-icons/AWS-Architecture-Icons_EPS_20200430.a8ee3992514c16602e1ead879f1bdceaf1c405a1.zip) (EPS, legacy pipeline).

## 18.02.22 Icons
Created using: [PNG,+SVG,+EPS_18.02.22.zip](https://s3-us-west-2.amazonaws.com/awswebanddesign/Architecture+Icons/AWS-Arch-Icon-Sets_Feb-18/PNG%2C+SVG%2C+EPS_18.02.22.zip) (legacy pipeline).

# Using the stencils

There are two ways to install stencils into OmniGraffle (thanks to [@voxpelli](https://twitter.com/voxpelli/status/1105536267352264705) for pointing out I don't include instructions on how to use the stencil files.)

## Installing a stencil

1. Double click on the stencil file, it will open in OmniGraffle
2. You can then move the stencil to make it available for future use

## Installing all the stencils

1. Use terminal to open the OmniGraffle stencil directory in Finder (for OmniGraffle 7.x) `open $HOME/Library/Containers/com.omnigroup.OmniGraffle7.MacAppStore/Data/Library/Application\ Support/The\ Omni\ Group/OmniGraffle/Stencils`
2. Create a directory called `AWS` or whatever works for you.
3. Copy the stencil files corresponding to the version of the icons you want to use into the `AWS` folder you just created. For the `26.04.30` set you can copy the whole folder — the `Architecture Service Icons/` and `Resource Icons/` sub-folders become stencil groups inside OmniGraffle.
4. Open OmniGraffle and create awesome diagrams using the AWS Architecture Icons ;-)

> **Tip:** each icon carries its service/resource name. To see the names in the
> Stencils sidebar, switch that stencil to **list mode** (the view toggle at the
> bottom of the stencil window) — grid mode shows the artwork only.

Any problems, omissions or suggestions then feel free to either raise an [issue](https://github.com/davidfsmith/AWS-OmniGraffle-Stencils/issues) or better yet, fork the repo, make the change and open a PR.

# Creating stencil files

## 26.04.30 and newer (SVG packs) — `convert.py`

Modern AWS packs are SVG, so the converter renders each icon to a **vector PDF**
with `rsvg-convert` and embeds it in a `.gstencil`. Human-readable names are
derived from the filenames automatically (no `meta.txt` to maintain), `&` and
other special characters are handled, and the common AWS filename "stutters"
(e.g. `Amazon-MSK_Amazon-MSK-Connect` → "Amazon MSK Connect") are cleaned up.

### Dependencies

	brew install librsvg

(`rsvg-convert` is the only requirement; Python 3.9+ is used to run the script.)

### Steps

1. Download the latest **Asset Package** from [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) and unzip it. You should end up with a tree like:

		aws-source-2026/
		  Architecture-Service-Icons_04302026/
		  Resource-Icons_04302026/
		  Architecture-Group-Icons_04302026/
		  Category-Icons_04302026/

2. Run the converter, pointing it at that folder and a dated output directory:

		./convert.py aws-source-2026 26.04.30

That's it. Useful options:

	./convert.py aws-source-2026 26.04.30 --combined       # also build "AWS All Icons.gstencil"
	./convert.py aws-source-2026 26.04.30 --only combined  # build ONLY the big stencil
	./convert.py aws-source-2026 26.04.30 --clean          # wipe output first
	./convert.py aws-source-2026 26.04.30 --only service   # one collection (repeatable)
	./convert.py aws-source-2026 26.04.30 --png            # embed PNG instead of vector PDF
	./convert.py aws-source-2026 26.04.30 --service-size 48 --category-size 32

The combined stencil contains the same 812 icons as the per-category sets, just
gathered into a single file (it's ~1.7&nbsp;MB and duplicates the artwork, so it's
opt-in rather than built by default).

Light icons are used by default; the `_Dark` variants are skipped.

## 20.04.30 and older (EPS packs) — `convert.sh` (legacy)

The original pipeline for the EPS packs. Kept for reproducing the older sets.

### Dependencies

	brew install xpdf
	brew install --cask mactex

Then install the Ghostscript package from [MacTex packages](http://www.tug.org/mactex/morepackages.html)

### Steps

Download the EPS icons, unzip, replace all instances of `&` with `and` in directories and filenames, then run `convert.sh`:

	./convert.sh ~/Downloads/AWS-Architecture-Icons_EPS_20200430/EPS\ Light 20.04.30

For images where there is no meta data you will need to update the `meta.txt` with the additional information.

# Finally

Massive thanks to [azuenko](https://github.com/azuenko) for the original automation magic ;-)
