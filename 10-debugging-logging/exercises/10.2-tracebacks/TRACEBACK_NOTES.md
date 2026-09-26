# Reading and Diagnosing Python Tracebacks: 10.2 Guide

A Python traceback is a snapshot of the execution call stack at the exact instant an unhandled exception halts execution. Master engineers read tracebacks **bottom-up**:
1. **The Final Line**: Tells you *what* failed (the exception type and error message).
2. **The Bottom Frame**: Tells you *where* execution died (file, line number, and code snippet).
3. **The Preceding Frames**: Tells you *how* the program reached that point (the sequence of function calls that routed bad data into the failing frame).

---

## 1. KeyError: `'email'`

### The Traceback
```text
Traceback (most recent call last):
  File "traceback_exercises.py", line 110, in <module>
    func()
  File "traceback_exercises.py", line 100, in <lambda>
    ("KeyError", lambda: get_user_primary_email({"name": "Alex", "contact": {"phone": "555-0100"}})),
  File "traceback_exercises.py", line 30, in get_user_primary_email
    return _extract_email_field(user_record)
  File "traceback_exercises.py", line 22, in _extract_email_field
    return profile["contact"]["email"]
           ~~~~~~~~~~~~~~~~~~^^^^^^^^^
KeyError: 'email'
```

### How to Read & Locate the Fault
- **Bottom line**: `KeyError: 'email'`. This means code attempted to access a dictionary key named `'email'`, but that key is not in the dictionary.
- **Fault frame**: Line 22 inside `_extract_email_field`: `profile["contact"]["email"]`. The Python 3.11+ squiggly underline (`^^^^^^^^^`) pinpoints the exact subscript operation that failed.
- **Trace the caller**: Line 30 shows `get_user_primary_email` called `_extract_email_field(user_record)`. Line 100 reveals the caller supplied a dictionary with `"contact": {"phone": "555-0100"}` which omitted `"email"`.
- **Diagnostic Remedy**: Use `profile["contact"].get("email")` or validate schema before lookup.

---

## 2. ZeroDivisionError: `division by zero`

### The Traceback
```text
Traceback (most recent call last):
  File "traceback_exercises.py", line 110, in <module>
    func()
  File "traceback_exercises.py", line 101, in <lambda>
    ("ZeroDivisionError", lambda: compute_average_metric("latency_ms", [])),
  File "traceback_exercises.py", line 46, in compute_average_metric
    return _calculate_mean(values)
  File "traceback_exercises.py", line 38, in _calculate_mean
    return sum(samples) / len(samples)
           ~~~~~~~~~~~~~^~~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

### How to Read & Locate the Fault
- **Bottom line**: `ZeroDivisionError: division by zero`. The denominator of a division expression evaluated to `0`.
- **Fault frame**: Line 38 inside `_calculate_mean`: `sum(samples) / len(samples)`. The caret points to `/` where `len(samples)` is the divisor.
- **Trace the caller**: In line 101, `compute_average_metric` received `[]` (an empty list). `len([])` is `0`.
- **Diagnostic Remedy**: Check `if not samples: return 0.0` or raise an explicit domain error before attempting division.

---

## 3. TypeError: `can only concatenate str (not "int") to str`

### The Traceback
```text
Traceback (most recent call last):
  File "traceback_exercises.py", line 110, in <module>
    func()
  File "traceback_exercises.py", line 102, in <lambda>
    ("TypeError", lambda: format_order_summary("ORD-9821", 5)),
  File "traceback_exercises.py", line 62, in format_order_summary
    header = _compose_header(prefix, item_count)
  File "traceback_exercises.py", line 54, in _compose_header
    return prefix + count
           ~~~~~~~^~~~~~~
TypeError: can only concatenate str (not "int") to str
```

### How to Read & Locate the Fault
- **Bottom line**: `TypeError: can only concatenate str (not "int") to str`. The `+` operator was used between a string and an integer.
- **Fault frame**: Line 54 in `_compose_header`: `return prefix + count`. Python requires explicit type conversion when concatenating strings and numbers.
- **Trace the caller**: Line 62 in `format_order_summary` passes `item_count=5` directly into `_compose_header` without conversion.
- **Diagnostic Remedy**: Use f-strings (`f"{prefix}{count}"`) or explicitly cast `str(count)`.

---

## 4. IndexError: `list index out of range`

### The Traceback
```text
Traceback (most recent call last):
  File "traceback_exercises.py", line 110, in <module>
    func()
  File "traceback_exercises.py", line 103, in <lambda>
    ("IndexError", lambda: get_pipeline_stage(["lint", "test", "build"], 10)),
  File "traceback_exercises.py", line 79, in get_pipeline_stage
    return _resolve_stage(stages, stage_index)
  File "traceback_exercises.py", line 71, in _resolve_stage
    return stages[index]
           ~~~~~~^^^^^^^
IndexError: list index out of range
```

### How to Read & Locate the Fault
- **Bottom line**: `IndexError: list index out of range`. An integer index was requested that lies outside `0 <= index < len(stages)`.
- **Fault frame**: Line 71 in `_resolve_stage`: `return stages[index]`.
- **Trace the caller**: Line 103 passed `stages` with 3 items (`len == 3`, valid indices 0, 1, 2) and `stage_index = 10`.
- **Diagnostic Remedy**: Validate `0 <= stage_index < len(stages)` or handle default stage fallback.

---

## 5. AttributeError: `'NoneType' object has no attribute 'send'`

### The Traceback
```text
Traceback (most recent call last):
  File "traceback_exercises.py", line 110, in <module>
    func()
  File "traceback_exercises.py", line 104, in <lambda>
    ("AttributeError", lambda: dispatch_notification({"name": "Sam"}, None)),
  File "traceback_exercises.py", line 95, in dispatch_notification
    return _execute_send(notifier, recipient["name"])
  File "traceback_exercises.py", line 87, in _execute_send
    return notifier.send(f"Hello, {recipient_name}")
           ^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'send'
```

### How to Read & Locate the Fault
- **Bottom line**: `AttributeError: 'NoneType' object has no attribute 'send'`. You tried to call `.send()` on a variable that evaluates to `None`.
- **Fault frame**: Line 87 in `_execute_send`: `notifier.send(...)`.
- **Trace the caller**: Line 104 passed `None` as the `notifier` parameter into `dispatch_notification`. Line 95 forwarded that `None` to `_execute_send`.
- **Diagnostic Remedy**: Check if dependency injection failed, instantiate a null-object fallback, or raise a clean `ValueError("Notifier cannot be None")` at boundary entry.
