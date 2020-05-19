d=$(date "+%a, %d %b %Y at %H hours, %M mins, %S seconds %Z")
export BUILD_DATE="${d}"
exec "$@"