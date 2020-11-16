class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """

        for i in range(len(nums)):


            for j in range(i+1, len(nums)):
                print(str(i)+":"+str(nums[i])+'-'+str(nums[j]))

                if nums[i] + nums[j] == target:
                    return [i, j]
#
a = Solution().twoSum(nums=[2, 7, 11, 15], target=9)
print(a)
# nums=[2, 7, 11, 15]
#
# for i in range(len(nums)-1):
#          print(i)
         # print(nums[i])


# class Solution:
#     def twoSum(self, nums, target):
#         """
#         :type nums: List[int]
#         :type target: int
#         :rtype: List[int]
#         """
#         hashmap = {}
#         for index, num in enumerate(nums):
#             another_num = target - num
#             if another_num in hashmap:
#                 return [hashmap[another_num], index]
#             hashmap[num] = index
#
#         return None
#
# Solution().twoSum(nums=[2, 7, 11, 15], target=9)