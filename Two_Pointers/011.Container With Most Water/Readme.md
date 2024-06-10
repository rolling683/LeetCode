### 11. Container With Most Water
#### method: Two pointer
    左指針指向0, 右指針指向height.size()-1。因為此時最寬, 為可能答案。

    移動指針時, 因寬度縮短, 需移動長度較短的板子才可能使面積變大, 因面積受限於較短的板子。

[Leetcode problem](https://leetcode.com/problems/container-with-most-water)
