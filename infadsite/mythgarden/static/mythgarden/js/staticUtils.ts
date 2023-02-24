// fn: check if a value is a string, and throw an error if not
function getStrOrError (str: any): string {
  if (typeof str !== 'string') {
    throw new Error(`Expected string, got ${typeof str}`)
  }

  return str
}

function isDeepEqual (o1: object, o2: object): boolean {
  const [keys1, keys2] = [o1, o2].map(o => Object.keys(o))

  if (!areKeysEqual(keys1, keys2)) return false

  return keys1.every(key => {
    // @ts-expect-error - we assume we can index into these objects with their own keys
    const [v1, v2] = [o1, o2].map(o => o[key])
    if (isObject(v1) && isObject(v2)) {
      if (!isDeepEqual(v1, v2)) return false
    } else {
      if (v1 !== v2) return false
    }

    return true
  })
}

function areKeysEqual (keys1: string[], keys2: string[]): boolean {
  return keys1.every(key => keys2.includes(key)) && keys2.every(key => keys1.includes(key))
}

function isObject (value: any): boolean {
  return value != null && typeof value === 'object'
}

export {
  getStrOrError,
  isDeepEqual
}
