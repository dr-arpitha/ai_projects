import pexpect

# start a child  process with spawn
# It just echos  geeksforgeeks
child = pexpect.spawn("echo geeksforgeeks")
child.sendline("hai")

# prints he matched index of string.
print(child.expect(["hai", "welcome", "geeksforgeeks"]))
