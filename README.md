# Record for later
Record live streaming videos for later!

## Docker
docker run --restart=always --detach --name=`whoami`-rfl --volume=`pwd`/streams:/rfl/streams --volume=`pwd`/config.yaml:/rfl/config.yaml jonghwanhyeon/rfl