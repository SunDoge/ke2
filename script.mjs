#!/usr/bin/env zx

await $`cat pyproject.toml`

let branch = await $`git branch --show-current`
// await $`dep deploy --branch=${branch}`
console.log(branch)

await Promise.all([
  $`sleep 1; echo 1`,
  $`sleep 2; echo 2`,
  $`sleep 3; echo 3`,
])

let name = 'foo bar'
await $`mkdir /tmp/${name}`
