import { Row, Card, Form, Space, Typography } from 'antd'
import { Layout } from '../../components/layout'
import { CustomInput } from '../../components/custom-input'
import { PasswordInput } from '../../components/password-input'
import { CustomButton } from '../../components/custom-button'
import { Link, useNavigate } from 'react-router-dom'
import { Paths } from '../../paths'
import { useSelector } from 'react-redux'
import { selectUser } from '../../features/auth/authSlice'
import { useState } from 'react'
import { User } from "@prisma/client";
import { ErrorMessage } from '../../components/error-message'
import { isErrorWithMessage } from '../../utils/is-error-with-message'
import { useRegisterMutation } from '../../app/services/auth'

type RegisterData = Omit<User, "id"> & { confirmPassword: string }

export const Register = () => {

  const navigate = useNavigate();
  const user = useSelector(selectUser);
  const [error, setError] = useState('');
  const [registerUser] = useRegisterMutation()

  const register = async (data: RegisterData) => {
    try {
      await registerUser(data).unwrap();
      navigate(`${Paths.home}`)
    } catch (error) {
      const maybeError = isErrorWithMessage(error);

      if (maybeError) {
        setError(error.data.message)
      } else {
        setError('unknown message')
      }
    }
  }

  return (
    <Layout>
      <Row align="middle" justify="center">
        <Card title="Sign in" style={{ width: "30rem" }}>
          <Form onFinish={register}>
            <CustomInput name={'name'} placeholder={'Enter your name'}></CustomInput>
            <CustomInput name={'email'} placeholder={'Enter your email'} type="email"></CustomInput>
            <PasswordInput name={'password'} placeholder={'Enter your password'}></PasswordInput>
            <PasswordInput name={'confirmPassword'} placeholder={'Confirm your password'}></PasswordInput>
            <CustomButton type="primary" htmlType='submit'> Sign in</CustomButton>
          </Form>
          <Space direction='vertical' size='large'>
            <Typography.Text>
              Do you have an account? <Link to={Paths.login}>Log in</Link>
            </Typography.Text>
            <ErrorMessage message={error} />
          </Space>
        </Card>
      </Row>
    </Layout>
  )
}

