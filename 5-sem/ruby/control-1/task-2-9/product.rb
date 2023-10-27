class Product
    attr_accessor :id, :name, :upc, :manufacturer, :price, :shelf_life, :quantity
  
    def initialize(id, name, upc, manufacturer, price, shelf_life, quantity)
      @id = id
      @name = name
      @upc = upc
      @manufacturer = manufacturer
      @price = price
      @shelf_life = shelf_life
      @quantity = quantity
    end

    def initialize(*args)
        @id = args[0]
        @name = args[1]
        @upc = args[2]
        @manufacturer = args[3]
        @price = args[4]
        @shelf_life = args[5]
        @quantity = args[6]
    end
  
    def toString
      "ID: #{@id}, Name: #{@name}, UPC: #{@upc}, Manufacturer: #{@manufacturer}, Price: #{@price}, Shelf Life: #{@shelf_life}, Quantity: #{@quantity}"
    end

    def set_id(id)
        @id = id
    end

    def get_id
        @id
    end

    def set_name(name)
        @name = name
    end

    def get_name
        @name
    end

    def set_upc(upc)
        @upc = upc
    end

    def get_upc
        @upc
    end

    def set_manufacturer(manufacturer)
        @manufacturer = manufacturer
    end

    def get_manufacturer
        @manufacturer
    end

    def set_price(price)
        @price = price
    end

    def get_price
        @price
    end

    def set_shelf_life(shelf_life)
        @shelf_life = shelf_life
    end

    def get_shelf_life
        @shelf_life
    end

    def set_quantity(quantity)
        @quantity = quantity
    end

    def get_quantity
        @quantity
    end    
  end
  