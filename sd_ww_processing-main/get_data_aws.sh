while read file; do
  echo "$file"
  test=$(echo $file | sed 's:.*/::')
  echo $test
  aws s3 cp $file $test
done <links.txt