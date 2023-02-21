1. install selenium IDE onto chrome
2. modify the IDE configuration: 
   - enable "Allow access to file URLs"
3. open the *.side project and please modify the file directory of some test steps onto the IDE

*** the steps run on selenium ide is different from the one run on python program. On the python program, We need to make sure the element exists before we can verify/asset/click it. We seldom need to care about it when we run the test onto selenium IDE.
*** clear mongo data first before we run the tests, i.e. python clear_data.py
*** modify a user account onto the selenium IDE project files and py files. 

The py file is basically exported from the selenium IDE. Need to make some modification manually:

replace the test level setup/teardown functions with the class level ones. 

i.e.

replase 

  def setup(self):

  def teardown(self):


with following lines

  @classmethod
  def setup_class(cls):
    cls.driver = webdriver.Chrome()
    cls.vars = {}

  @classmethod
  def teardown_class(cls):
    cls.driver.quit() 


test cases:
copo-erga-p01 : with correct erga manifest with image upload
copo-erga-p02 : with correct erga manifest with permit upload
copo-erga-f01 : with incorrect erga manifest
