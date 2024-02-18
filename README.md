# elelementary

a markup langauge/ui building system in python i havent had time to complete

meant to be like html and css though much less useful
![image](https://user-images.githubusercontent.com/88392191/209446520-dd3fe709-b882-4893-9d1e-7735bf8ad369.png)

# usage 
**warning:** this is an unfinished project, I wouldn't use it. but if you insist:

- install dependencies

  ```pip install pyray```
  
- clone the code to your directory

  ```git clone https://github.com/9EED/elelementary```
  
- create a .elel a .spsp and a .py file

  using your file explorer
  
- import the engine script in your python 

  ```py
  import elelementary as el
  ```

- load the elel and spsp files

  ```py
  elel_file = el.load_elel('example.elel')
  sps_file = el.load_sps('example.spsp')
  ```

- bind the spsp to the elel

  ```py
  elel_file.bind(sps_file)
  ```

- code your programs layout in the elel file

- style it in the spsp file

- run the program through the python file

  ```py
  elel_file.open()
  ```


or just edit the example


quite the scuffed project ngl <br>
ive been too busy with school to work on it
