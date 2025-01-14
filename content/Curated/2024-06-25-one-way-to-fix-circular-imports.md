Title: One way to fix Python circular imports
Tags: python, troubleshooting
Author: Ned Batchelder
Url: https://nedbatchelder.com/blog/202405/one_way_to_fix_python_circular_imports.html
Summary: I've already encountered issues regarding circular imports, most of the time it was related to typings only (two modules referencing types from each others) and is easily resolved using a `if TYPE_CHECKING:` block. For other cases I try my best to shape my modules in a way that it does not require circular imports. In the following article I discovered another way to overcome circular imports that I could not have think about simply by defering imported names lookup.
