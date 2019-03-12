AWS-OmniGraffle-Stencils
========================

If use OmniGraffle and AWS - these stencils are for you.

Omnigraffle compatible versions of the [AWS simple icons](https://aws.amazon.com/architecture/icons/).

## 19.02.07
Only the light background icons have been converted.  Last updated using: [AWS-Architecture-Icons_EPS_20190207](https://d1.awsstatic.com/webteam/architecture-icons/AWS-Architecture-Icons_EPS_20190207.2b615daa2f47347ca46e67c56bd35be79cea5bee.zip)

## 18.02.22
Last updated using: [PNG,+SVG,+EPS_18.02.22.zip](https://s3-us-west-2.amazonaws.com/awswebanddesign/Architecture+Icons/AWS-Arch-Icon-Sets_Feb-18/PNG%2C+SVG%2C+EPS_18.02.22.zip)

# Converting Icons

## Installing epstopdf

	brew cask install mactex
	
Then install the Ghostscript package from [MacTex packages](http://www.tug.org/mactex/morepackages.html)

## Steps

* Download the latest AWS icons and unzip into the same directory as `convert.sh`
* run `./convert.sh <unzipped AWS icons directory>`

Time passes, but you should find that you'll have just the converted PDF files left in the AWS icons directory.

* Manually add the PDF files to the stencil files.

Dull but works, drag and dropping the PDF files into a stencil template can be a bit hit and miss.  I've found the best way is to copy and paste in each icon, then group, name and add on the anchor points.

Dull, but handy.

# Todo

Automate the process more, sadly trying to open the .gstencil plist files results in an error and needs more research.  Additional file renaming steps for the converted icons as well as creating a basic URL look up / list of files would help reduce some of the manual steps.