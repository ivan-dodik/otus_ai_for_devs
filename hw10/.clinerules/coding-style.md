# Cline Betaflight Coding Style Rules

These rules are derived from `betaflight_coding_style.md` and MUST be followed when writing or modifying C code in this project.

## Formatting

### Indentation
- [1TBS](https://en.wikipedia.org/wiki/Indentation_style#Variant:_1TBS_(OTBS)) (K&R variant) indent style
- **4 space indent**, NO hard tabs (all tabs replaced by spaces)

### Curly Braces

#### Functions
- Opening and closing braces at the beginning of the next line, followed by a line break.

```
int function(int x)
{
    body of function
}
```

#### Non-function statement blocks (if, switch, for, etc.)
- Opening brace last on the same line.
- Closing brace on the line after the last statement.
- If followed by `else` / `else if` — on the same line as closing brace.

```
if (x is true) {
    we do y
} else {
    we do z
}
```

#### Braces are REQUIRED
- **NEVER omit braces** for single-statement `if`/`else` blocks. This prevents future bugs when statements are added.

### Line Length
- Stay within **120 columns**.
- Never exceed **140 columns** (hard limit for readability on GitHub).

### Spaces
- **Space after** these keywords: `if`, `switch`, `case`, `for`, `do`, `while`
- **No space after**: `sizeof`, `typeof`, `alignof`, `__attribute__`
- One space around (each side of) binary/ternary operators: `=  +  -  <  >  *  /  %  |  &  ^  <=  >=  ==  !=  ?  :`
- **No space after** unary operators: `&  *  +  -  ~  !  sizeof  typeof  alignof  __attribute__  defined`
- **No space before** postfix `++` / `--`
- **No space after** prefix `++` / `--`
- **No space** around `.` and `->` structure member operators
- `*` and `&` (pointer/reference): **no space** between operator and variable name — adjacent to **name**, not type:
  - `char *linux_banner;`
  - `memparse(char *ptr, char **retptr);`

## typedef

- **Enums without count**: trailing comma after **last** element (so diffs show only added lines):

```
typedef enum {
    MSP_RESULT_ACK = 1,
    MSP_RESULT_ERROR = -1,
} mspResult_e;
```

- **Enums WITH count**: count MUST be the **last item** (automatically maintained). Do NOT compute afterward (e.g., `PID_CONTROLLER_LUX_FLOAT + 1` is BAD).

```
typedef enum {
    PID_CONTROLLER_MW23 = 0,
    PID_CONTROLLER_MWREWRITE,
    PID_CONTROLLER_LUX_FLOAT,
    PID_COUNT
} pidControllerType_e;
```

- **Struct typedefs**: MUST include struct name for forward references:

```
typedef struct motorMixer_s {
    float throttle;
    float yaw;
} motorMixer_t;
```

## Variables

### Naming
- Descriptive **lowerCamelCase** for functions, variables, arguments.
- CLI-accessible config variables: **all_lowercase_with_underscores**.
- Variable names should be **nouns**.
- Simple temp vars with tiny scope may be short per common practice (e.g., `i` in `for` loop).

### Declarations
- **Avoid global variables**.
- Declare at the **top of the smallest scope** where used.
- Use distinct variables for unrelated uses — **do not reuse** variables.
- One blank line follows declarations.
- To reduce scope: create a block (curly braces), e.g., inside a `case` branch.
- Variables may be declared at point of first use when limited use.

### Initialization
- **NO lazy initialization**. In flight controller code, it's better to spend extra ms before takeoff than during flight.
- Use an explicit **init** function.

## Data Types
- Be explicit about types — **don't trust implicit type casting**.
- Angles: beware representation (float degrees vs uint8_t decidegrees).
- **Avoid implicit double conversions** — use only float-argument functions.
- Float constants MUST use `"f"` suffix: `1.0f`, `3.1415926f`.
- Use `sin_approx()` / `cos_approx()` from `common/math.h` instead of `sin()` / `cos()`.

## Functions

### Naming
- Boolean-returning methods: named as a question, should NOT change state: `isOkToArm()`.
- Verb or verb-phrase names: `deletePage()`, `save()`. Tell the system to "do something with something".
- Non-static functions: **prefix by class**: `baroUpdate()` (NOT `updateCompass()`).
- Groups acting on an "object": share same prefix:
  - `biQuadFilterApply()`, `biQuadFilterInit()`, `biQuadIsReady()`

### Parameter Order
- Data flows **right-to-left** (as in `memcpy(void *dst, const void *src, size_t size)`).
- When group functions act on an "object": **object is first parameter** for ALL functions in group.

```
// GOOD
float biQuadFilterApply(biquad_t *state, float sample);
void biQuadNewLpf(biquad_t *state, float filterCutFreq, uint32_t refreshRate);

// BAD
float biQuadFilterApply(float sample, biquad_t *state);
```

### Declarations
- Internal (file-local) functions: declare **`static`** (or `STATIC_UNIT_TESTED` for test access).
- Non-static functions: declaration in **one .h file**.
- Don't expose more than necessary — not even types.
- Use `MODULENAME_INTERNALS_` pattern for test-only internals:

```
// In .h file:
#ifdef MODULENAME_INTERNALS_
… declarations …
#endif

// In module .c and test file:
#define MODULENAME_INTERNALS_
#include "module.h"
```

### Implementation
- Keep functions **short and distinctive**.
- Think about unit tests when defining functions. Ideally implement tests **before** the function.
- **NEVER** put multiple statements on a single line.
- **NEVER** put multiple assignments on a single line / single statement.
- Prefer `const` over pre-processor macros for constants.
- Enforce const-correctness (catches param order errors like `memcpy` at compile time).
- Read HW data **once per call**, preferably all in one place. Store in local variable.
- Use `for` loops for iteration (rather than `do` / `while`).
- **AVOID**: `continue`, `goto`, multiple `return` from a function, multiple `break` inside a `case`.
  - In rare cases justified, but only when you understand alternatives and still have strong reason.
- Parentheses: use **only where required** by operator precedence or compiler warnings.
  - **Exception**: ternary conditional operator — condition **enclosed in parentheses**:
    ```
    pidStabilisationEnabled = (pidControllerState == PID_STABILISATION_ON) ? true : false;
    ```

## Includes
- Each file **includes its own dependencies** — don't rely on transitive includes.
- **Don't include unused headers**.
- Use **`#pragma once`** (preferred over include guards).

## Documentation Comments
- All new code files, structs, enums, and functions: add comment **at top describing purpose**.
- PRs modifying existing items: add comment if not present, update if applicable to changes.
- May be omitted for trivial / self-explanatory items.
- Example file-level comment:

```c
/* This file contains code used to send DSHOT commands using the STM timer's burst DMA functionality.
 * It uses DMA to alter timer PWM duty cycle. For an alternative approach, see `drivers/dshot_bitbang.c`
 * for a DSHOT implementation that uses GPIO bitbanging.
 */
```

## Other
- **NO trailing whitespace** at end of lines or blank lines.
- Take maximum advantage of compile-time checking — strict warnings.
- **Don't call or reference "upwards"**: device drivers (bottom layer) must not call anything outside device drivers.
- **No target-specific code** (e.g., `#ifdef CC3D`) outside `src/main/target` directory.
- Use `typedef void handlerFunc(void);` — easier to read than pointer-to-function typedef.
- **Code should be spherical**: minimise public interfaces relative to functionality. Public interfaces easy to use, implementation hidden.
- **Code based on sound principles** (mathematical, physical, CS), not heuristics. Tests too.
- **Guidelines, not tramlines**: these rules can be broken when there is a **good reason**.