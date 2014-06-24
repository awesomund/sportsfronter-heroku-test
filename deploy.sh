#!/usr/bin/env bash

# Stop script on fail, only last command in pipeline counts
set -eo pipefail;

appserver=dokku@app.iterate.no
app=sportsfronter

install_gitsubtree() {
  local defaultpath="$1"
  if [[ -f $defaultpath ]]; then
    sudo install -m 755 $defaultpath "$(git --exec-path)"/git-subtree
    echo "SUCCESS: Installed git-subtree"
  else
    echo >&2 "ERROR: Happy path did not work. Setup git-subtree manually."
    exit 1
  fi
}
install_gitsubtree_linux () {
  install_gitsubtree "/usr/share/doc/git/contrib/subtree/git-subtree.sh"
}
install_gitsubtree_osx () {
  install_gitsubtree "/usr/local/share/git-core/contrib/subtree/git-subtree.sh"
}

verify_dependencies() {
  if ! git help -a | grep " subtree" >/dev/null; then
    echo "Dependency git-subtree missing. Trying to install…"
    case "$OSTYPE" in
      darwin*)
        echo "Mac OSX detected."
        install_gitsubtree_osx
        echo ""
        ;;
      linux*)
        echo "Linux detected."
        install_gitsubtree_linux
        echo ""
        ;;
      *)
        echo >&2 "ERROR: Could not recognize $OSTYPE. Setup git-subtree manually"
        exit 1
        ;;
    esac
  fi
}
verify_gitremotes() {
  git remote -v | grep "app" >/dev/null || git remote add app $appserver:$app
}
deploy() {
  remote="$1"; path="$2"
  git push -f $remote `git subtree split --prefix $path HEAD`:refs/heads/master
}


# Clunky, but portable way to get the dir of this script.
pushd `dirname $0`> /dev/null
scriptpath=`pwd`
popd > /dev/null

# Get the project root directory by traversing upwards till finding .git dir
projectdir=""
runner="$scriptpath"
while [ "$runner" != "/" ]; do
  findresult=`find "$runner" -maxdepth 1 -name ".git"`
  if [[ -n "$findresult" ]]; then
    projectdir="$runner"
    break
  fi
  runner=`dirname "$runner"`
done

cd "$projectdir"
verify_dependencies
verify_gitremotes

case "$1" in
  help|-h)
    echo "Usage : deploy"
    ;;
  *)
    deploy app webapp
    ;;

esac

