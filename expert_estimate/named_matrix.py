from typing import List, Iterable, Dict, Any, Union, Tuple

class NamedMatrix:
    def __init__(self, rows: List[Iterable[str]], cols: List[Iterable[str]], default: Any = None) -> None:
        self.rows = rows
        self.cols = cols

        self._default = default
        self._data: Dict[str, Dict[str, Any]] = { r: {c: default for c in self.cols} for r in self.rows }

    def __getitem__(self, key: Union[str, Tuple[str, str]]) -> Any:
        if isinstance(key, tuple):
            row, col = key
            return self._data[row][col]
        return self._data[key]

    def __setitem__(self, key: Union[str, Tuple[str, str]], value: Any) -> None:
        if isinstance(key, tuple):
            row, col = key
            self._data[row][col] = value
        else:
            if not isinstance(value, dict):
                raise TypeError("Присваивание строке требует словарь {col: value}")
            self._data[key] = dict(value)

    def __contains__(self, key: Union[str, Tuple[str, str]]) -> bool:
        if isinstance(key, tuple):
            row, col = key
            return row in self._data and col in self._data[row]
        return key in self._data

    def __iter__(self):
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def row(self, name: str) -> Dict[str, Any]:
        return self._data[name]

    def col(self, name: str) -> Dict[str, Any]:
        return {r: self._data[r][name] for r in self.rows}
    
    
    def __add__(self, other: "NamedMatrix") -> "NamedMatrix":
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Размеры/имена матриц не совпадают")

        result = NamedMatrix(self.rows, self.cols, self._default)
        for r in self.rows:
            for c in self.cols:
                result[r, c] = self[r, c] + other[r, c]
        return result
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NamedMatrix):
            return NotImplemented
        return (
            self.rows == other.rows
            and self.cols == other.cols
            and all(self[r, c] == other[r, c] for r in self.rows for c in self.cols)
        )
    
    def copy(self) -> "NamedMatrix":
        result = NamedMatrix(self.rows, self.cols, self._default)
        for r in self.rows:
            for c in self.cols:
                result[r, c] = self[r, c]
        return result

    def transpose(self) -> "NamedMatrix":
        result = NamedMatrix(self.cols, self.rows, self._default)
        for r in self.rows:
            for c in self.cols:
                result[c, r] = self[r, c]
        return result

    def sum(self) -> Any:
        return sum(self.values())
    
    def __repr__(self) -> str:
        return f"NamedMatrix(rows={self.rows}, cols={self.cols})"

    def __str__(self) -> str:
        row_w = max([len("")] + [len(r) for r in self.rows])
        col_ws = {
            c: max(len(c), max((len(str(self._data[r][c])) for r in self.rows), default=0))
            for c in self.cols
        }

        header = " " * (row_w + 2) + "  ".join(c.center(col_ws[c]) for c in self.cols)
        lines = [header]

        for r in self.rows:
            cells = "  ".join(
                str(self._data[r][c]).center(col_ws[c]) for c in self.cols
            )
            lines.append(f"{r.rjust(row_w)}  {cells}")

        return "\n".join(lines)

    def items(self):
        for r in self.rows:
            for c in self.cols:
                yield (r, c), self._data[r][c]

    def values(self):
        for r in self.rows:
            for c in self.cols:
                yield self._data[r][c]
