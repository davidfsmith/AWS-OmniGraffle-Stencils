AWS-OmniGraffle-Stencils
========================

If use OmniGraffle and AWS - these stencils are for you.

Omnigraffle compatible versions of the [AWS simple icons](https://aws.amazon.com/architecture/icons/).

## 20.04.30 Icons
Light background icons have been converted.  Created using [AWS-Architecture-Icons_EPS_20200430](https://d1.awsstatic.com/webteam/architecture-icons/AWS-Architecture-Icons_EPS_20200430.a8ee3992514c16602e1ead879f1bdceaf1c405a1.zip)

## 18.02.22 Icons
Created using: [PNG,+SVG,+EPS_18.02.22.zip](https://s3-us-west-2.amazonaws.com/awswebanddesign/Architecture+Icons/AWS-Arch-Icon-Sets_Feb-18/PNG%2C+SVG%2C+EPS_18.02.22.zip)

# Using the stencils

There are two ways to install stencils into Omnigraffle (thanks to [@voxpelli](https://twitter.com/voxpelli/status/1105536267352264705) for pointing out I don't include instructions on how to use the stencil files.)

## Installing a stencil

1. Double click on the stencil file, it will open in Omnigraffle
2. You can then move the stencil to make it available for future use

## Installing all the stencils

1. Use terminal to open the Omnigraffle stencil directory in Finder (for Omnigraffle 7.x) `open $HOME/Library/Containers/com.omnigroup.OmniGraffle7.MacAppStore/Data/Library/Application\ Support/The\ Omni\ Group/OmniGraffle/Stencils`
2. Create a directory called `AWS` or whatever works for you.
3. Copy the stencil files corresponding to the version of the icons you want to use into the `AWS` folder you just created
4. Open Omnigraffle and create awesome diagrams using the AWS Architecture Icons ;-)

Any problems, ommissions ot suggestions then feel free to either raise an [issue](https://github.com/davidfsmith/AWS-OmniGraffle-Stencils/issues) or better yet, fork the repo, make the change and open a PR.

# Creating stencil files

## Converting Icons (OSX)

### Installing Dependencies

	brew install xpdf
	brew install --cask mactex

Then install the Ghostscript package from [MacTex packages](http://www.tug.org/mactex/morepackages.html)

### Steps

Download the latest AWS icons from [AWS simple icons](https://aws.amazon.com/architecture/icons/), unzip the file and then replace all instances of `&` with `and` in directories and filenames, then run `convert.sh` :

	./convert.sh ~/Downloads/AWS-Architecture-Icons_EPS_20200430/EPS\ Light 20.04.30

Time passes....

For images where there is no meta data you will need to update the `meta.txt` with the additional information.

# Finally

Massive thanks to [azuenko](https://github.com/azuenko) for the automation magic ;-)
