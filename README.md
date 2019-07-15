# Record for later
Record live streaming videos for later!

## Docker
    docker run \
      --restart=always \
      --detach \
      --env UID=`id --user` \
      --env GID=`id --group` \
      --volume=`pwd`/config.yaml:/rfl/config.yaml \
      --volume=`pwd`/streams:/rfl/streams \
      jonghwanhyeon/rfl
