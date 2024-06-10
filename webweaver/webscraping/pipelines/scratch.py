#!/bin/env python3
# import phonenumbers
# import re

# nums = [
#     '1-604-345-1231',
#     '(604) 345-1959',
#     '1 (604) 345-1959',
#     '1-(604) 345-1959',
#     '6043451515',
#     '(604)3453959',
#     '(604)344-1454'
#     '60434518373'
# ]

# for num in nums:

#     print(phonenumbers.is_valid_number(phonenumbers.parse(num, 'CA')))

nums = [1, 2, 3, 4]
for i in range(0, len(nums)):
    print(i)

def bleh() -> None:
    """
    Do not return anything, modify nums1 in-place instead.
    """
    m = 3
    n = 3
    nums1 = [1,2,3,0,0,0]
    nums2 = [2,5,6]

    nums1 = [num for num in nums1 if num != 0]
    nums1.extend(nums2)
    nums1.sort()

    print(nums1)


def bleh2():
    nums1 = [1,2,3,0,0,0]
    nums2 = [2,5,6]
    m = 3
    n = 3

    for i in range(m,m+n):
        nums1[i]=nums2[i-m]
        print(nums1[i], nums2[i-m])
    nums1.sort()
    # a, b, write_index = m-1, n-1, m + n - 1

    # while b >= 0:
    #     if a >= 0 and nums1[a] > nums2[b]:
    #         nums1[write_index] = nums1[a]
    #         a -= 1
    #     else:
    #         nums1[write_index] = nums2[b]
    #         b -= 1

    #     write_index -= 1
    print(nums1)


# bleh2()

