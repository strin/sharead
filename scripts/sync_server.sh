TARGET=appx
rsync -vLr --exclude=server/shareread.sqlite --exclude=server/upload server $TARGET:~/papertroll
