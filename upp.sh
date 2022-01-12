cd $(pwd)

# pre-commit run -a

update_time=`date "+%Y-%m-%d %H:%M:%S"`

# add
git add .
echo git add .

# commit
if [ ! -n "$1" ]; then
    git commit -m "update: $update_time"
    echo git commit -m "update: $update_time"
else
    git commit -m "$1"
    echo git commit -m "$1"
fi


# push
checkout_name=`git symbolic-ref HEAD 2>/dev/null | cut -d"/" -f 3`
git push origin $checkout_name
echo git push origin $checkout_name
