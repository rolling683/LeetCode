class Solution {
public:
    vector<vector<int>> res;
    vector<vector<int>> threeSum(vector<int>& nums) {
        sort(nums.begin(), nums.end());
        for(int i = 0; i < nums.size(); i++){
            if(i > 0 && nums[i] == nums[i-1]) continue;
            twoSum(nums, i);
        }
        return res;
    }
    void twoSum(vector<int>& nums, int n){
        int target = -nums[n];
        int left = n + 1;
        int right = nums.size() - 1;
        while(left < right){
            int sum = nums[left] + nums[right];
            if(sum < target){
                left++;
            }
            else if (sum > target){
                right--;
            }
            else{
                vector<int> tmp = {nums[n], nums[left], nums[right]};
                res.push_back(tmp);
                while(left < right && nums[left] == tmp[1]) left++;
                while(left < right && nums[right] == tmp[2]) right--;
            }
        }
    }
};