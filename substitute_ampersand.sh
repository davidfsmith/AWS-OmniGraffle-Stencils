for file in `find . -name "*&*"`
do
	mv -v "$file" "${file/&/and}"
done
